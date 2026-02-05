#!/usr/bin/env python3
"""
RAG Manager - Sistema de memória de longo prazo
"""

import chromadb
from chromadb.config import Settings
import os
import json
from datetime import datetime

class RAGManager:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "chroma-db"),
            port=int(os.getenv("CHROMA_PORT", "8000")),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collections = {
            "knowledge": self._get_or_create_collection("personal_knowledge_base"),
            "conversations": self._get_or_create_collection("conversation_history"),
            "documents": self._get_or_create_collection("document_store")
        }
    
    def _get_or_create_collection(self, name):
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"created_at": datetime.now().isoformat()}
            )
    
    def add_knowledge(self, text, metadata=None):
        """Adiciona conhecimento à base"""
        self.collections["knowledge"].add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[f"knowledge_{datetime.now().timestamp()}"]
        )
    
    def add_conversation(self, user_msg, bot_msg, metadata=None):
        """Salva conversa"""
        conv_text = f"User: {user_msg}\nBot: {bot_msg}"
        self.collections["conversations"].add(
            documents=[conv_text],
            metadatas=[metadata or {}],
            ids=[f"conv_{datetime.now().timestamp()}"]
        )
    
    def add_document(self, content, filename, metadata=None):
        """Adiciona documento processado"""
        meta = metadata or {}
        meta["filename"] = filename
        meta["added_at"] = datetime.now().isoformat()
        
        self.collections["documents"].add(
            documents=[content],
            metadatas=[meta],
            ids=[f"doc_{filename}_{datetime.now().timestamp()}"]
        )
    
    def search(self, query, collection="knowledge", n_results=5):
        """Busca semântica"""
        results = self.collections[collection].query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_context(self, query, max_results=5):
        """Obtém contexto relevante de todas as coleções"""
        context = []
        
        for name, collection in self.collections.items():
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=max_results
                )
                if results["documents"]:
                    context.append({
                        "source": name,
                        "results": results["documents"][0]
                    })
            except:
                continue
        
        return context

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python rag_manager.py <comando> <args>")
        print("Comandos: add, search, context")
        sys.exit(1)
    
    manager = RAGManager()
    command = sys.argv[1]
    
    if command == "add":
        text = sys.argv[2]
        manager.add_knowledge(text)
        print("Conhecimento adicionado")
    
    elif command == "search":
        query = sys.argv[2]
        results = manager.search(query)
        print(json.dumps(results, indent=2))
    
    elif command == "context":
        query = sys.argv[2]
        context = manager.get_context(query)
        print(json.dumps(context, indent=2, ensure_ascii=False))
