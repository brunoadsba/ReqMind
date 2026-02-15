import os
import json
import logging
import networkx as nx
from typing import List, Dict, Optional
from .types import Triple

logger = logging.getLogger(__name__)

class GraphStore:
    """Wrapper para NetworkX com persistência em JSON"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.graph = nx.DiGraph()
        self._load()

    def _load(self):
        """Carrega o grafo do disco"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                logger.info(f"Grafo carregado: {self.graph.number_of_nodes()} nós, {self.graph.number_of_edges()} arestas")
            except Exception as e:
                logger.error(f"Erro ao carregar grafo: {e}")
                self.graph = nx.DiGraph()
        else:
            logger.info("Nenhum grafo existente encontrado. Iniciando novo.")
            self.graph = nx.DiGraph()

    def _save(self):
        """Salva o grafo no disco"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = nx.node_link_data(self.graph)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar grafo: {e}")

    def add_triples(self, triples: List[Triple], memory_id: str):
        """Adiciona triplas ao grafo, linkando à memória de origem"""
        changed = False
        for triple in triples:
            # Nodes
            if not self.graph.has_node(triple.subject):
                self.graph.add_node(triple.subject, type="entity")
                changed = True
            if not self.graph.has_node(triple.object):
                self.graph.add_node(triple.object, type="entity")
                changed = True
            
            # Edge
            self.graph.add_edge(
                triple.subject, 
                triple.object, 
                relation=triple.predicate,
                memory_id=memory_id,
                confidence=triple.confidence
            )
            changed = True
        
        if changed:
            self._save()

    def get_related_entities(self, query_entities: List[str], depth: int = 1) -> List[str]:
        """Retorna entidades conectadas às entidades da query (simples traversal)"""
        related = set()
        for entity in query_entities:
            if self.graph.has_node(entity):
                # Vizinhos diretos (outgoing)
                neighbors = list(self.graph.neighbors(entity))
                related.update(neighbors)
                
                # Se depth > 1, expandir... (KISS: depth 1 for now)
        
        return list(related)

    def pagerank_search(self, query_entities: List[str], top_k: int = 5) -> Dict[str, float]:
        """
        Executa Personalized PageRank a partir das entidades da query.
        Retorna top_k nós mais relevantes.
        """
        if not self.graph.number_of_nodes():
            return {}
            
        # Personalization vector: 1.0 para entidades da query, 0.0 para resto
        personalization = {node: 0.0 for node in self.graph.nodes()}
        start_nodes = [node for node in query_entities if node in self.graph]
        
        if not start_nodes:
            return {}

        weight = 1.0 / len(start_nodes)
        for node in start_nodes:
            personalization[node] = weight

        try:
            scores = nx.pagerank(self.graph, personalization=personalization)
            # Ordenar por score
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            # Filtrar os próprios nós da query para achar *novas* conexões
            results = {node: score for node, score in sorted_scores if node not in query_entities}
            # Pegar top_k
            return dict(list(results.items())[:top_k])
        except Exception as e:
            logger.error(f"Erro no PageRank: {e}")
            return {}
