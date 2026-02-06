"""RAG system with OpenAI embeddings for travel data."""

import os
import json
import numpy as np
from openai import OpenAI
from data import FLIGHTS, HOTELS, ACTIVITIES, TRAVEL_GUIDES


client = None


def get_client():
    global client
    if client is None:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client


def get_embedding(text: str) -> list[float]:
    """Get embedding for a text string."""
    response = get_client().embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class TravelRAG:
    """RAG system for travel data."""

    def __init__(self):
        self.documents = []
        self.embeddings = []
        self._indexed = False

    def index_data(self):
        """Index all travel data with embeddings."""
        if self._indexed:
            return

        print("Indexing travel data...")

        # Index flights
        for flight in FLIGHTS:
            doc = {
                "type": "flight",
                "id": flight["id"],
                "content": f"Flight from {flight['from']} to {flight['to']} on {flight['airline']}. "
                          f"Departure: {flight['departure']}, Arrival: {flight['arrival']}. "
                          f"Price: ${flight['price']} {flight['class']} class.",
                "data": flight
            }
            self.documents.append(doc)

        # Index hotels
        for hotel in HOTELS:
            doc = {
                "type": "hotel",
                "id": hotel["id"],
                "content": f"{hotel['name']} hotel in {hotel['city']}. "
                          f"Rating: {hotel['rating']} stars. ${hotel['price_per_night']} per night. "
                          f"Amenities: {', '.join(hotel['amenities'])}. {hotel['description']}",
                "data": hotel
            }
            self.documents.append(doc)

        # Index activities
        for activity in ACTIVITIES:
            doc = {
                "type": "activity",
                "id": activity["id"],
                "content": f"{activity['name']} in {activity['city']}. "
                          f"Duration: {activity['duration']}, Price: ${activity['price']}. "
                          f"{activity['description']}",
                "data": activity
            }
            self.documents.append(doc)

        # Index travel guides
        for city, guide in TRAVEL_GUIDES.items():
            doc = {
                "type": "guide",
                "id": city.lower(),
                "content": f"Travel guide for {city}. Best time to visit: {guide['best_time']}. "
                          f"Currency: {guide['currency']}. Language: {guide['language']}. "
                          f"Must see: {', '.join(guide['must_see'])}. "
                          f"Tips: {' '.join(guide['tips'])}",
                "data": {"city": city, **guide}
            }
            self.documents.append(doc)

        # Generate embeddings for all documents
        print(f"Generating embeddings for {len(self.documents)} documents...")
        for doc in self.documents:
            embedding = get_embedding(doc["content"])
            self.embeddings.append(embedding)

        self._indexed = True
        print("Indexing complete!")

    def search(self, query: str, top_k: int = 5, threshold: float = 0.3) -> list[dict]:
        """Search for relevant documents."""
        if not self._indexed:
            self.index_data()

        query_embedding = get_embedding(query)

        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            sim = cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, sim))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top results above threshold
        results = []
        for idx, sim in similarities[:top_k]:
            if sim >= threshold:
                doc = self.documents[idx].copy()
                doc["similarity"] = sim
                results.append(doc)

        return results

    def get_context(self, query: str) -> tuple[str, bool]:
        """
        Get context for a query.
        Returns (context_string, found_in_rag)
        """
        results = self.search(query)

        if not results:
            return "", False

        context_parts = []
        for result in results:
            context_parts.append(f"[{result['type'].upper()}] {result['content']}")

        return "\n\n".join(context_parts), True


# Singleton instance
_rag_instance = None


def get_rag() -> TravelRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TravelRAG()
    return _rag_instance
