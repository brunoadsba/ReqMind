import chromadb
from chromadb.utils import embedding_functions
import os
import logging
from typing import List, Dict, Optional
from .types import Memory

logger = logging.getLogger(__name__)

class VectorStore:
    """Wrapper para ChromaDB Lite"""
    
    def __init__(self, storage_path: str, collection_name: str = "hippocampus_memories"):
        self.storage_path = storage_path
        self.collection_name = collection_name
        
        # Garante diretório
        os.makedirs(storage_path, exist_ok=True)
        
        # Cliente persistente
        self.client = chromadb.PersistentClient(path=storage_path)
        
        # Embedding function (Default: all-MiniLM-L6-v2, download automático na 1ª vez)
        # Pode ser trocado por OpenAI se configurado
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        logger.info(f"ChromaDB iniciado em {storage_path}, coleção: {collection_name}")

    def add_memory(self, memory: Memory):
        """Adiciona memória ao vetor"""
        # Metadata flat para Chroma
        meta = {
            "type": memory.type.value,
            "user_id": memory.user_id,
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance_score
        }
        # Adicionar campos extras do metadata original
        for k, v in memory.metadata.items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
        
        self.collection.upsert(
            ids=[memory.id],
            documents=[memory.content],
            metadatas=[meta]
        )

    def search(self, query: str, user_id: str, top_k: int = 5) -> List[Dict]:
        """Busca semântica"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id}  # Filtro por usuário
        )
        
        # Formatar retorno
        hits = []
        if results['ids']:
            ids = results['ids'][0]
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            dists = results['distances'][0]
            
            for i in range(len(ids)):
                hits.append({
                    "id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i],
                    "score": 1.0 - dists[i]  # Distance to similarity (aprox)
                })
        
        return hits
