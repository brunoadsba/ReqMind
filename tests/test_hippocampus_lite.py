import pytest
import os
import shutil
import sys
import os
# Add src to path if not present (for local tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    from features.hippocampus.client import HippocampusClient, MemoryType
except ImportError:
    from src.features.hippocampus.client import HippocampusClient, MemoryType


@pytest.fixture
def clean_hippocampus():
    """Limpa diretório de dados do Hippocampus antes/depois do teste"""
    data_dir = "tests/data/hippocampus_test"
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    yield data_dir
    # Cleanup
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

def test_hippocampus_lite_flow(clean_hippocampus):
    """Teste básico do fluxo de memória (Lite)"""
    client = HippocampusClient(clean_hippocampus)
    
    # 1. Remember (Episodic)
    mem_id = client.remember(
        content="O usuário Bruno prefere respostas curtas.",
        user_id="user_123",
        memory_type=MemoryType.EPISODIC
    )
    assert mem_id is not None
    
    # 2. Recall
    context = client.recall("Como o Bruno gosta das respostas?", user_id="user_123")
    
    # Verifica se recuperou
    assert "Bruno prefere respostas curtas" in context
    assert "[EPISODIC]" in context

def test_hippocampus_persistence(clean_hippocampus):
    """Teste de persistência (simulando restart)"""
    # Sessão 1
    client1 = HippocampusClient(clean_hippocampus)
    client1.remember("O projeto é sobre LLMs.", "user_123", MemoryType.SEMANTIC)
    
    # Sessão 2 (novo cliente no mesmo dir)
    client2 = HippocampusClient(clean_hippocampus)
    context = client2.recall("Sobre o que é o projeto?", "user_123")
    
    assert "sobre LLMs" in context
