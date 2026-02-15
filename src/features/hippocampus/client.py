import logging
import uuid
import os
from typing import List, Dict, Optional
from datetime import datetime

from .types import Memory, MemoryType, Triple
from .vector_store import VectorStore
from .graph_store import GraphStore

logger = logging.getLogger(__name__)

class HippocampusClient:
    """
    Cliente principal do sistema de memória HippocampAI (Lite).
    Orquestra ChromaDB (Vetores) e NetworkX (Grafo).
    """
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
        # Caminhos de armazenamento
        vector_path = os.path.join(data_dir, "chroma_db")
        graph_path = os.path.join(data_dir, "knowledge_graph.json")
        
        # Inicializar stores
        self.vector_store = VectorStore(vector_path)
        self.graph_store = GraphStore(graph_path)
        
        logger.info("HippocampusClient inicializado (Lite Version)")

    def remember(self, content: str, user_id: str, memory_type: MemoryType = MemoryType.EPISODIC, metadata: Dict = None):
        """
        Armazena uma nova memória.
        1. Cria objeto Memory
        2. Salva no Vector Store
        3. (Futuro) Extrai triplas e salva no Graph Store
        """
        mem_id = str(uuid.uuid4())
        
        # TODO: Extração de Entidades/Triplas via LLM (fase posterior)
        # Por enquanto, extração dummy para teste
        entities = [] 
        triples = []
        
        memory = Memory(
            id=mem_id,
            user_id=user_id,
            content=content,
            type=memory_type,
            metadata=metadata or {},
            entities=entities,
            triples=triples,
            timestamp=datetime.now()
        )
        
        # 1. Vector Store
        self.vector_store.add_memory(memory)
        
        # 2. Graph Store (Se houver triplas)
        if triples:
            self.graph_store.add_triples(triples, mem_id)
            
        logger.info(f"Memória armazenada: {mem_id} type={memory_type}")
        return mem_id

    def recall(self, query: str, user_id: str, top_k: int = 5) -> str:
        """
        Recupera contexto relevante para a query.
        Retorna string formatada para o LLM.
        """
        # 1. Busca Vetorial
        vector_results = self.vector_store.search(query, user_id, top_k=top_k)
        
        # TODO: 2. Busca no Grafo (PageRank das entidades da query)
        # graph_results = self.graph_store.pagerank_search(...)
        
        # TODO: 3. RRF Fusion (Combinar resultados)
        
        # Por enquanto, retorna apenas vetorial formatado
        if not vector_results:
            return ""
            
        context_lines = []
        for res in vector_results:
            # Formato: [TIpo] Conteúdo (Score)
            m_type = res['metadata'].get('type', 'info')
            content = res['content']
            context_lines.append(f"[{m_type.upper()}] {content}")
            
        return "\n".join(context_lines)
