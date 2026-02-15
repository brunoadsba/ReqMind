from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

class MemoryType(str, Enum):
    EPISODIC = "episodic"      # Conversas, eventos (stream)
    SEMANTIC = "semantic"      # Fatos, preferências, regras (fatos isolados)
    PROCEDURAL = "procedural"  # Comportamentos, estilo (instruções de como agir)

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0

@dataclass
class Memory:
    id: str
    user_id: str
    content: str
    type: MemoryType
    timestamp: datetime = field(default_factory=datetime.now)
    entities: List[str] = field(default_factory=list)
    triples: List[Triple] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    session_id: Optional[str] = None
    importance_score: float = 0.5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "entities": self.entities,
            "triples": [{"subject": t.subject, "predicate": t.predicate, "object": t.object, "confidence": t.confidence} for t in self.triples],
            "session_id": self.session_id,
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            content=data["content"],
            type=MemoryType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            entities=data.get("entities", []),
            triples=[Triple(**t) for t in data.get("triples", [])],
            session_id=data.get("session_id"),
            importance_score=data.get("importance_score", 0.5),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data.get("last_accessed", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )
