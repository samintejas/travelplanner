import chromadb
from chromadb.config import Settings
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class ChromaClient:
    _instance: Optional["ChromaClient"] = None
    _client: Optional[chromadb.HttpClient] = None

    def __new__(cls, host: str = "chromadb", port: int = 8000):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(host, port)
        return cls._instance

    def _initialize(self, host: str, port: int, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                self._client = chromadb.HttpClient(
                    host=host,
                    port=port,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                    ),
                )
                # Test connection by listing collections
                self._client.list_collections()
                logger.info(f"Connected to ChromaDB at {host}:{port}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"ChromaDB connection attempt {attempt + 1} failed: {e}. Retrying in 2s...")
                    time.sleep(2)
                else:
                    logger.warning(f"Could not connect to ChromaDB after {max_retries} attempts: {e}. Using in-memory client.")
                    self._client = chromadb.Client(Settings(anonymized_telemetry=False))

    @property
    def client(self) -> chromadb.ClientAPI:
        return self._client

    def get_or_create_collection(self, name: str):
        return self._client.get_or_create_collection(name=name)

    def get_conversations_collection(self):
        return self.get_or_create_collection("conversations")

    def get_bookings_collection(self):
        return self.get_or_create_collection("bookings")

    def get_destinations_collection(self):
        return self.get_or_create_collection("destinations")

    def add_destination_docs(self, docs: list[dict]):
        """Add destination knowledge documents to the collection."""
        collection = self.get_destinations_collection()
        for doc in docs:
            collection.upsert(
                ids=[doc["id"]],
                documents=[doc["content"]],
                metadatas=[{
                    "destination": doc.get("destination", ""),
                    "category": doc.get("category", "general"),
                    "title": doc.get("title", ""),
                }],
            )
        logger.info(f"Added {len(docs)} destination documents")

    def query_destinations(self, query: str, destination: str = None, n_results: int = 5):
        collection = self.get_destinations_collection()
        try:
            where_filter = {"destination": destination} if destination else None
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )
            return results
        except Exception as e:
            logger.error(f"Error querying destinations: {e}")
            return {"documents": [], "metadatas": []}

    def add_conversation(self, session_id: str, messages: list[dict]):
        collection = self.get_conversations_collection()
        for i, msg in enumerate(messages):
            doc_id = f"{session_id}_{i}"
            collection.upsert(
                ids=[doc_id],
                documents=[msg["content"]],
                metadatas=[{
                    "session_id": session_id,
                    "role": msg["role"],
                    "index": i,
                }],
            )

    def add_booking(self, booking_id: str, booking_data: dict):
        collection = self.get_bookings_collection()
        doc_content = f"Booking for {booking_data.get('user_name', 'Unknown')} to {booking_data.get('destination', 'Unknown')}. Email: {booking_data.get('user_email', 'Unknown')}. Status: {booking_data.get('status', 'Unknown')}."
        collection.upsert(
            ids=[booking_id],
            documents=[doc_content],
            metadatas=[booking_data],
        )

    def query_conversations(self, query: str, n_results: int = 5):
        collection = self.get_conversations_collection()
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            return results
        except Exception as e:
            logger.error(f"Error querying conversations: {e}")
            return {"documents": [], "metadatas": []}

    def query_bookings(self, query: str, n_results: int = 5):
        collection = self.get_bookings_collection()
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            return results
        except Exception as e:
            logger.error(f"Error querying bookings: {e}")
            return {"documents": [], "metadatas": []}
