from .chroma_client import ChromaClient
from typing import List, Dict, Any


class TravelRetriever:
    def __init__(self, chroma_client: ChromaClient):
        self.chroma = chroma_client

    def retrieve_relevant_conversations(
        self, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        results = self.chroma.query_conversations(query, n_results)
        documents = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = (
                    results["metadatas"][0][i]
                    if results.get("metadatas") and results["metadatas"][0]
                    else {}
                )
                documents.append({
                    "content": doc,
                    "session_id": metadata.get("session_id", ""),
                    "role": metadata.get("role", ""),
                })
        return documents

    def retrieve_bookings(
        self, query: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        results = self.chroma.query_bookings(query, n_results)
        bookings = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = (
                    results["metadatas"][0][i]
                    if results.get("metadatas") and results["metadatas"][0]
                    else {}
                )
                bookings.append({
                    "content": doc,
                    "metadata": metadata,
                })
        return bookings

    def get_context_for_session(self, session_id: str) -> str:
        results = self.chroma.query_conversations(
            f"session:{session_id}", n_results=20
        )
        context_parts = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = (
                    results["metadatas"][0][i]
                    if results.get("metadatas") and results["metadatas"][0]
                    else {}
                )
                if metadata.get("session_id") == session_id:
                    role = metadata.get("role", "unknown")
                    context_parts.append(f"{role}: {doc}")
        return "\n".join(context_parts)
