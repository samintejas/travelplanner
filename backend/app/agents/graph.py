from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from .state import TravelState
from .nodes import (
    preference_collector,
    itinerary_planner,
    booking_agent,
    notification_agent,
)


def should_continue_preferences(state: TravelState) -> Literal["itinerary_planner", "preference_collector"]:
    """Determine if preferences are complete."""
    if state.get("preferences_complete", False):
        return "itinerary_planner"
    return "preference_collector"


def should_continue_itinerary(state: TravelState) -> Literal["booking_agent", "itinerary_planner"]:
    """Determine if itinerary is ready for booking."""
    if state.get("itinerary") is not None:
        return "booking_agent"
    return "itinerary_planner"


def should_continue_booking(state: TravelState) -> Literal["notification_agent", "booking_agent", "__end__"]:
    """Determine if booking is confirmed."""
    if state.get("booking_confirmed", False):
        return "notification_agent"
    return "booking_agent"


def create_travel_graph() -> StateGraph:
    """Create the travel planning workflow graph."""

    workflow = StateGraph(TravelState)

    # Add nodes
    workflow.add_node("preference_collector", preference_collector)
    workflow.add_node("itinerary_planner", itinerary_planner)
    workflow.add_node("booking_agent", booking_agent)
    workflow.add_node("notification_agent", notification_agent)

    # Set entry point
    workflow.set_entry_point("preference_collector")

    # Add conditional edges
    workflow.add_conditional_edges(
        "preference_collector",
        should_continue_preferences,
        {
            "itinerary_planner": "itinerary_planner",
            "preference_collector": END,  # Wait for user input
        }
    )

    workflow.add_conditional_edges(
        "itinerary_planner",
        should_continue_itinerary,
        {
            "booking_agent": END,  # Wait for user to review
            "itinerary_planner": END,
        }
    )

    workflow.add_conditional_edges(
        "booking_agent",
        should_continue_booking,
        {
            "notification_agent": "notification_agent",
            "booking_agent": END,  # Wait for user input
            "__end__": END,
        }
    )

    workflow.add_edge("notification_agent", END)

    return workflow.compile()


class TravelGraph:
    def __init__(self):
        self.graph = create_travel_graph()
        self.sessions: Dict[str, TravelState] = {}

    def get_initial_state(self, session_id: str) -> TravelState:
        """Create initial state for a new session."""
        return TravelState(
            messages=[],
            session_id=session_id,
            preferences={},
            preferences_complete=False,
            itinerary=None,
            selected_flights=[],
            selected_hotels=[],
            selected_activities=[],
            booking_confirmed=False,
            booking_details=None,
            current_agent="preference_collector",
            needs_user_input=True,
            response="",
        )

    def get_or_create_session(self, session_id: str) -> TravelState:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = self.get_initial_state(session_id)
        return self.sessions[session_id]

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a user message and return the response."""
        state = self.get_or_create_session(session_id)

        # Add user message
        state["messages"] = list(state["messages"]) + [HumanMessage(content=message)]

        # Determine which agent to run based on current state
        if state.get("booking_confirmed"):
            # Already booked, just respond
            return {
                "response": "Your booking is already confirmed! Is there anything else I can help you with?",
                "session_id": session_id,
                "itinerary": state.get("itinerary"),
                "booking_ready": False,
            }

        # Run the appropriate agent
        current_agent = state.get("current_agent", "preference_collector")

        if current_agent == "preference_collector":
            from .nodes import preference_collector
            result = preference_collector(state)
        elif current_agent == "itinerary_planner":
            from .nodes import itinerary_planner
            result = itinerary_planner(state)
        elif current_agent == "booking_agent":
            from .nodes import booking_agent
            result = booking_agent(state)
        else:
            from .nodes import preference_collector
            result = preference_collector(state)

        # Update session state
        for key, value in result.items():
            if key == "messages":
                state["messages"] = list(state["messages"]) + list(value)
            else:
                state[key] = value

        self.sessions[session_id] = state

        # Check if we should advance to next stage
        if result.get("preferences_complete") and current_agent == "preference_collector":
            # Move to itinerary planning
            state["current_agent"] = "itinerary_planner"
            itinerary_result = itinerary_planner(state)
            for key, value in itinerary_result.items():
                if key == "messages":
                    state["messages"] = list(state["messages"]) + list(value)
                else:
                    state[key] = value
            self.sessions[session_id] = state
            return {
                "response": result["response"] + "\n\n" + itinerary_result["response"],
                "session_id": session_id,
                "itinerary": state.get("itinerary"),
                "booking_ready": True,
            }

        if result.get("booking_confirmed"):
            # Send notification
            state["current_agent"] = "notification_agent"
            notif_result = notification_agent(state)
            for key, value in notif_result.items():
                if key == "messages":
                    state["messages"] = list(state["messages"]) + list(value)
                else:
                    state[key] = value
            self.sessions[session_id] = state
            return {
                "response": notif_result["response"],
                "session_id": session_id,
                "itinerary": state.get("itinerary"),
                "booking_ready": False,
            }

        return {
            "response": result["response"],
            "session_id": session_id,
            "itinerary": state.get("itinerary"),
            "booking_ready": state.get("itinerary") is not None and not state.get("booking_confirmed"),
        }

    def get_session_state(self, session_id: str) -> TravelState | None:
        """Get the current state of a session."""
        return self.sessions.get(session_id)

    def confirm_booking(self, session_id: str, user_name: str, user_email: str) -> Dict[str, Any]:
        """Confirm a booking for a session."""
        state = self.get_or_create_session(session_id)

        if not state.get("itinerary"):
            return {"error": "No itinerary to book"}

        state["booking_details"] = {
            "user_name": user_name,
            "user_email": user_email,
            "itinerary": state["itinerary"],
            "status": "confirmed",
        }
        state["booking_confirmed"] = True

        # Send notification
        notif_result = notification_agent(state)
        for key, value in notif_result.items():
            if key == "messages":
                state["messages"] = list(state["messages"]) + list(value)
            else:
                state[key] = value

        self.sessions[session_id] = state

        return {
            "response": notif_result["response"],
            "session_id": session_id,
            "itinerary": state.get("itinerary"),
            "booking_confirmed": True,
        }
