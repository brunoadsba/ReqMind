#!/bin/bash
# Script de parada do Assistente Digital
# Uso: ./scripts/stop.sh

set -e

BASE_DIR="/home/brunoadsba/assistente"
PID_FILE="${BASE_DIR}/bot.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Parando Assistente Digital...${NC}"

# Verificar se arquivo PID existe
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}📍 Encerrando processo ${PID}...${NC}"
        kill $PID || true
        sleep 2
        
        # Verificar se ainda está rodando
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${RED}⚠️  Forçando encerramento...${NC}"
            kill -9 $PID || true
        fi
        
        echo -e "${GREEN}✅ Bot parado${NC}"
    else
        echo -e "${YELLOW}⚠️  Processo ${PID} não está rodando${NC}"
    fi
    rm -f "$PID_FILE"
else
    # Tentar encontrar e matar pelo nome
    if pgrep -f "bot_simple.py" > /dev/null; then
        echo -e "${YELLOW}📍 Parando todas as instâncias...${NC}"
        pkill -f "bot_simple.py" || true
        echo -e "${GREEN}✅ Bot parado${NC}"
    else
        echo -e "${YELLOW}⚠️  Nenhuma instância encontrada${NC}"
    fi
fi
