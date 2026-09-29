"""
Memory management module for DevRecall utilizing Hindsight Agent Memory.
Provides both direct Hindsight client integration and local fallback for offline demos.
"""

import os
import json
import logging
import warnings
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from hindsight_client import Hindsight
    HINDSIGHT_INSTALLED = True
except ImportError:
    HINDSIGHT_INSTALLED = False

logger = logging.getLogger("devrecall.memory")


class DevMemory:
    """
    Manages long-term environment memory for developer agents.
    Communicates with Vectorize Hindsight API or local resilient memory bank.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        bank_id: str = "devrecall-bank",
        storage_file: str = ".devrecall/memory.json"
    ):
        self.bank_id = bank_id
        self.base_url = base_url or os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")
        self.storage_file = storage_file
        self.client: Optional[Any] = None
        self.using_remote_hindsight = False

        self._initialize_client()
        self._ensure_local_storage()

    def _initialize_client(self):
        """Attempts to connect to the Hindsight service."""
        if HINDSIGHT_INSTALLED:
            client = None
            try:
                client = Hindsight(base_url=self.base_url, timeout=1.0)
                client.get_version()
                self.client = client
                self.using_remote_hindsight = True
                logger.info(f"Connected to Hindsight server at {self.base_url}")
            except Exception:
                if client is not None:
                    try:
                        client.close()
                    except Exception:
                        pass
                self.client = None
                self.using_remote_hindsight = False
                logger.info("Hindsight server unreachable. Running with resilient local memory engine.")

    def _ensure_local_storage(self):
        """Ensures the local directory and storage file exist."""
        os.makedirs(os.path.dirname(self.storage_file) or ".", exist_ok=True)
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump({"bank_id": self.bank_id, "memories": []}, f, indent=2)

    def retain(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retain a memory into Hindsight.
        Stores environment facts, shell constraints, port mappings, and tool habits.
        """
        tags = tags or ["environment", "dev"]
        timestamp = datetime.now(timezone.utc).isoformat()

        if self.using_remote_hindsight and self.client:
            try:
                response = self.client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    context=context,
                    tags=tags
                )
                return {
                    "source": "hindsight-cloud",
                    "status": "success",
                    "content": content,
                    "tags": tags,
                    "details": str(response)
                }
            except Exception as e:
                logger.warning(f"Remote retain failed ({e}). Falling back to local store.")

        # Local fallback retain logic
        with open(self.storage_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        memory_item = {
            "id": f"mem_{len(data.get('memories', [])) + 1}",
            "content": content,
            "context": context,
            "tags": tags,
            "timestamp": timestamp
        }

        # Prevent duplicate identical entries
        if not any(m.get("content") == content for m in data.get("memories", [])):
            data["memories"].append(memory_item)
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        return {
            "source": "hindsight-local",
            "status": "retained",
            "content": content,
            "tags": tags,
            "timestamp": timestamp
        }

    def recall(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories from Hindsight given a query.
        Returns matching environment quirks, rules, and prior configurations.
        """
        if self.using_remote_hindsight and self.client:
            try:
                response = self.client.recall(
                    bank_id=self.bank_id,
                    query=query
                )
                # Parse remote recall response
                results = []
                if hasattr(response, "results"):
                    for item in response.results:
                        results.append({
                            "content": getattr(item, "text", str(item)),
                            "relevance": getattr(item, "score", 1.0),
                            "source": "hindsight-remote"
                        })
                return results
            except Exception as e:
                logger.warning(f"Remote recall failed ({e}). Falling back to local store.")

        # Local fallback semantic / keyword recall logic
        with open(self.storage_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        query_terms = set(query.lower().split())
        scored = []
        for mem in data.get("memories", []):
            content_lower = mem.get("content", "").lower()
            tags_lower = [t.lower() for t in mem.get("tags", [])]

            score = 0
            for term in query_terms:
                if term in content_lower:
                    score += 2
                if any(term in t for t in tags_lower):
                    score += 3

            # Add fuzzy match weight
            if score > 0 or len(query_terms) == 0:
                scored.append((score, mem))

        # Sort by relevance score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": s[1].get("id"),
                "content": s[1].get("content"),
                "tags": s[1].get("tags"),
                "timestamp": s[1].get("timestamp"),
                "relevance_score": s[0],
                "source": "hindsight-memory-bank"
            }
            for s in scored[:max_results]
        ]

    def list_all(self) -> List[Dict[str, Any]]:
        """List all memories currently in the bank."""
        if not os.path.exists(self.storage_file):
            return []
        with open(self.storage_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("memories", [])

    def clear(self):
        """Clears all retained memories from the bank."""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump({"bank_id": self.bank_id, "memories": []}, f, indent=2)
