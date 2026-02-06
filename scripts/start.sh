#!/bin/bash
# Script de inicialização do Assistente Digital
# Uso: ./scripts/start.sh

set -e

# Diretório base = pasta do projeto (onde está o script/../)
BASE_DIR="${BASE_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$BASE_DIR"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🤖 Iniciando Assistente Digital...${NC}"

# Forçar uso da implementação pura do charset_normalizer para evitar segfaults
export CHARSET_NORMALIZER_PURE_PYTHON=1

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado em venv/${NC}"
    exit 1
fi

# Ativar ambiente virtual
echo -e "${YELLOW}📦 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    echo -e "${YELLOW}💡 Copie .env.example para .env e configure suas chaves${NC}"
    exit 1
fi

# Criar diretórios de dados se não existirem
mkdir -p data
mkdir -p tmp

# Verificar se há instância rodando (python ou python3 + bot_simple.py)
if pgrep -f "python3?.*bot_simple\.py" > /dev/null; then
    echo -e "${YELLOW}⚠️  Bot já está rodando. Parando instância anterior...${NC}"
    pkill -f "python3?.*bot_simple\.py" || true
    sleep 2
fi

echo -e "${GREEN}✅ Configuração OK!${NC}"
echo -e "${YELLOW}🚀 Iniciando bot...${NC}"

# Iniciar o bot com o Python do venv (evita ctypes/pandas do sistema)
export PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}"
"${BASE_DIR}/venv/bin/python" "${BASE_DIR}/src/bot_simple.py" &
PID=$!

# Salvar PID
echo $PID > "${BASE_DIR}/bot.pid"

echo -e "${GREEN}✅ Bot iniciado com PID: ${PID}${NC}"
echo -e "${YELLOW}📋 Logs: tail -f ${BASE_DIR}/bot.log${NC}"
echo -e "${YELLOW}🛑 Para parar: ./scripts/stop.sh${NC}"

# Aguardar um pouco e verificar se está rodando
sleep 3
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}✅ Bot está rodando normalmente${NC}"
else
    echo -e "${RED}❌ Bot parou inesperadamente. Verifique os logs.${NC}"
    exit 1
fi
