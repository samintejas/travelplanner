"""OpenAI LLM integration for Travel Concierge."""

import os
import json
from openai import OpenAI
from rag import get_rag
from web_search import search_web, format_web_results


client = None


def get_client():
    global client
    if client is None:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client


def _extract_destination_from_message(message: str) -> str:
    """Try to extract a destination from the user message."""
    import re
    message_lower = message.lower()

    # Look for "to X", "visit X", "trip to X", "travel to X", "go to X", "plan for X"
    patterns = [
        r'(?:trip|travel|go|visit|going|plan|planning|fly|flying)\s+(?:to|for)\s+([a-zA-Z\s]+?)(?:\s+(?:for|in|on|with|next|this)|[,.\?!]|$)',
        r'(?:want to|like to|planning to)\s+(?:visit|go to|see|explore)\s+([a-zA-Z\s]+?)(?:\s+(?:for|in|on|with)|[,.\?!]|$)',
        r'^([a-zA-Z\s]+?)\s+(?:trip|travel|vacation|holiday)',
    ]

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            dest = match.group(1).strip()
            # Filter out common non-destination words
            skip_words = ['a', 'the', 'my', 'our', 'this', 'that', 'some', 'any']
            if dest and dest not in skip_words and len(dest) > 2:
                return dest.title()

    return ""


SYSTEM_PROMPT = """You are a helpful travel concierge AI assistant. You help users plan trips to ANY destination in the world by:
- Understanding their travel preferences (destination, dates, budget, travel style)
- Finding flights, hotels, and activities
- Providing travel tips and recommendations
- Building and managing their itinerary

You can help plan trips to ANY city or country worldwide. Use the context provided (from our database or web search) to give accurate, up-to-date information.

When presenting bookable options from our system, include the item ID in parentheses (e.g., FL001, HT001, AC001).
For destinations not in our booking system, provide helpful recommendations and information from web search results.

Be concise, friendly, and helpful. Use markdown formatting for better readability.

IMPORTANT:
- You can help with ANY destination worldwide - not just pre-loaded cities
- When showing flights, hotels, or activities from our system, format them clearly with IDs
- For other destinations, provide detailed recommendations based on web search and your knowledge
- Extract user preferences like destination, budget, and travel style from the conversation
- If the user wants to confirm their booking, acknowledge it and mention the admin team has been notified
"""


def chat_with_context(
    user_message: str,
    chat_history: list[dict],
    preferences: dict,
    itinerary: dict
) -> tuple[str, dict]:
    """
    Generate a response using OpenAI with RAG context.
    Returns (response, extracted_info)
    """
    rag = get_rag()

    # Get RAG context
    rag_context, found_in_rag = rag.get_context(user_message)

    # Extract destination from message for web search
    destination = preferences.get("destination") or _extract_destination_from_message(user_message)

    # Try web search for destinations or if RAG didn't find much
    web_context = ""
    if destination:
        # Always do web search for travel info to supplement RAG
        search_queries = [
            f"{destination} travel guide tips",
            f"{destination} best hotels accommodation",
            f"{destination} things to do attractions",
        ]
        all_web_results = []
        for query in search_queries[:2]:  # Limit to 2 queries
            results = search_web(query, max_results=3)
            all_web_results.extend(results)

        if all_web_results:
            web_context = format_web_results(all_web_results[:6])

    # Build context message
    context_parts = []

    if rag_context:
        context_parts.append(f"TRAVEL DATA:\n{rag_context}")

    if web_context:
        context_parts.append(f"\n\nWEB SEARCH RESULTS:\n{web_context}")

    if preferences.get("destination") or preferences.get("budget"):
        pref_str = f"""
USER PREFERENCES:
- Destination: {preferences.get('destination', 'Not specified')}
- Origin: {preferences.get('origin', 'Not specified')}
- Dates: {preferences.get('start_date', 'Not specified')} to {preferences.get('end_date', 'Not specified')}
- Budget: ${preferences.get('budget', 'Not specified')}
- Travel Style: {preferences.get('travel_style', 'Not specified')}
"""
        context_parts.append(pref_str)

    if itinerary.get("flights") or itinerary.get("hotels") or itinerary.get("activities"):
        itin_str = f"""
CURRENT ITINERARY:
- Flights: {len(itinerary.get('flights', []))} booked
- Hotels: {len(itinerary.get('hotels', []))} booked
- Activities: {len(itinerary.get('activities', []))} booked
- Total Cost: ${itinerary.get('total_cost', 0):.2f}
"""
        context_parts.append(itin_str)

    context = "\n".join(context_parts)

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        messages.append({
            "role": "system",
            "content": f"CONTEXT:\n{context}"
        })

    # Add chat history (last 10 messages)
    for msg in chat_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current message
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    assistant_message = response.choices[0].message.content

    # Extract preferences using a separate call
    extracted = extract_preferences(user_message, preferences)

    return assistant_message, extracted


def extract_preferences(user_message: str, current_preferences: dict) -> dict:
    """Extract travel preferences from user message."""
    extraction_prompt = f"""Extract travel preferences from this message. Return a JSON object with only the fields that are mentioned.

Current preferences: {json.dumps(current_preferences)}

User message: "{user_message}"

Return JSON with any of these fields if mentioned:
- destination: string (city name)
- origin: string (departure city)
- start_date: string (YYYY-MM-DD format)
- end_date: string (YYYY-MM-DD format)
- budget: number (total budget in USD)
- travel_style: string (budget/moderate/luxury)

Only include fields that are explicitly or clearly implied in the message.
Return empty object {{}} if no preferences found.
"""

    try:
        response = get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        extracted = json.loads(response.choices[0].message.content)
        return extracted
    except Exception as e:
        print(f"Preference extraction error: {e}")
        return {}


def detect_intent(user_message: str) -> str:
    """Detect the intent of the user message."""
    message_lower = user_message.lower()

    if any(word in message_lower for word in ['confirm', 'book it', 'yes book', 'proceed', 'finalize']):
        return "confirm"
    if any(word in message_lower for word in ['flight', 'fly', 'airplane']):
        return "flight_search"
    if any(word in message_lower for word in ['hotel', 'stay', 'accommodation']):
        return "hotel_search"
    if any(word in message_lower for word in ['activity', 'activities', 'things to do', 'tour']):
        return "activity_search"
    if any(word in message_lower for word in ['guide', 'tips', 'advice', 'recommend']):
        return "guide"

    return "general"
