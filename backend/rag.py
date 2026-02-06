"""RAG system with ChromaDB for travel data persistence."""

import os
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from data import FLIGHTS, HOTELS, ACTIVITIES, TRAVEL_GUIDES


# ChromaDB connection
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))

openai_client = None


def get_openai_client():
    global openai_client
    if openai_client is None:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return openai_client


def get_chroma_client():
    """Get ChromaDB client."""
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        return client
    except Exception as e:
        print(f"ChromaDB connection failed: {e}, using in-memory fallback")
        return chromadb.Client()


def get_embedding(text: str) -> list[float]:
    """Get embedding for a text string using OpenAI."""
    response = get_openai_client().embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


class TravelRAG:
    """RAG system for travel data using ChromaDB."""

    def __init__(self):
        self.client = get_chroma_client()
        self.collection = None
        self._initialized = False

    def _get_or_create_collection(self):
        """Get or create the travel data collection."""
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name="travel_data",
                metadata={"description": "Travel concierge data"}
            )
        return self.collection

    def index_data(self):
        """Index all travel data with embeddings."""
        if self._initialized:
            return

        collection = self._get_or_create_collection()

        # Check if already indexed
        if collection.count() > 0:
            print(f"Collection already has {collection.count()} documents")
            self._initialized = True
            return

        print("Indexing travel data to ChromaDB...")

        documents = []
        metadatas = []
        ids = []
        embeddings = []

        # Index flights
        for flight in FLIGHTS:
            doc_id = f"flight_{flight['id']}"
            content = (
                f"Flight from {flight['from']} to {flight['to']} on {flight['airline']}. "
                f"Departure: {flight['departure']}, Arrival: {flight['arrival']}. "
                f"Price: ${flight['price']} {flight['class']} class."
            )
            documents.append(content)
            metadatas.append({"type": "flight", "item_id": flight["id"], "data": str(flight)})
            ids.append(doc_id)
            embeddings.append(get_embedding(content))

        # Index hotels
        for hotel in HOTELS:
            doc_id = f"hotel_{hotel['id']}"
            content = (
                f"{hotel['name']} hotel in {hotel['city']}. "
                f"Rating: {hotel['rating']} stars. ${hotel['price_per_night']} per night. "
                f"Amenities: {', '.join(hotel['amenities'])}. {hotel['description']}"
            )
            documents.append(content)
            metadatas.append({"type": "hotel", "item_id": hotel["id"], "data": str(hotel)})
            ids.append(doc_id)
            embeddings.append(get_embedding(content))

        # Index activities
        for activity in ACTIVITIES:
            doc_id = f"activity_{activity['id']}"
            content = (
                f"{activity['name']} in {activity['city']}. "
                f"Duration: {activity['duration']}, Price: ${activity['price']}. "
                f"{activity['description']}"
            )
            documents.append(content)
            metadatas.append({"type": "activity", "item_id": activity["id"], "data": str(activity)})
            ids.append(doc_id)
            embeddings.append(get_embedding(content))

        # Index travel guides
        for city, guide in TRAVEL_GUIDES.items():
            doc_id = f"guide_{city.lower()}"
            content = (
                f"Travel guide for {city}. Best time to visit: {guide['best_time']}. "
                f"Currency: {guide['currency']}. Language: {guide['language']}. "
                f"Must see: {', '.join(guide['must_see'])}. "
                f"Tips: {' '.join(guide['tips'])}"
            )
            documents.append(content)
            metadatas.append({"type": "guide", "item_id": city.lower(), "data": str(guide)})
            ids.append(doc_id)
            embeddings.append(get_embedding(content))

        # Add to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        self._initialized = True
        print(f"Indexed {len(documents)} documents to ChromaDB!")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant documents."""
        if not self._initialized:
            self.index_data()

        collection = self._get_or_create_collection()

        # Get query embedding
        query_embedding = get_embedding(query)

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def get_context(self, query: str) -> tuple[str, bool]:
        """
        Get context for a query.
        Returns (context_string, found_in_rag)
        """
        results = self.search(query)

        if not results:
            return "", False

        # Filter by distance (lower is better, threshold ~1.5 for relevance)
        relevant_results = [r for r in results if r.get('distance', 2) < 1.5]

        if not relevant_results:
            return "", False

        context_parts = []
        for result in relevant_results:
            doc_type = result['metadata'].get('type', 'unknown').upper()
            context_parts.append(f"[{doc_type}] {result['content']}")

        return "\n\n".join(context_parts), True

    def add_conversation(self, session_id: str, messages: list[dict]):
        """Add conversation to ChromaDB for admin RAG queries."""
        collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Customer conversations"}
        )

        for i, msg in enumerate(messages):
            doc_id = f"{session_id}_{i}"
            content = f"{msg['role']}: {msg['content']}"

            try:
                embedding = get_embedding(content)
                collection.upsert(
                    documents=[content],
                    metadatas=[{"session_id": session_id, "role": msg['role'], "timestamp": msg.get('timestamp', '')}],
                    ids=[doc_id],
                    embeddings=[embedding]
                )
            except Exception as e:
                print(f"Error adding conversation to ChromaDB: {e}")

    def search_conversations(self, query: str, session_id: str = None, top_k: int = 10) -> list[dict]:
        """Search conversations for admin queries."""
        try:
            collection = self.client.get_or_create_collection(name="conversations")

            query_embedding = get_embedding(query)

            where_filter = {"session_id": session_id} if session_id else None

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )

            formatted = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    })

            return formatted
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []


# Singleton instance
_rag_instance = None


def get_rag() -> TravelRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TravelRAG()
    return _rag_instance
