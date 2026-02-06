#!/bin/bash
# Verifica se o bot está rodando. Uso: ./scripts/status.sh ou make status

set -e

BASE_DIR="${BASE_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
PID_FILE="${BASE_DIR}/bot.pid"

# 1) Arquivo bot.pid (criado por start.sh)
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Bot rodando (PID: $PID)"
        exit 0
    fi
    echo "Bot não está rodando (bot.pid obsoleto)"
    rm -f "$PID_FILE"
    exit 0
fi

# 2) Processo Python executando bot_simple.py (python ou python3)
if pgrep -f "python3?.*bot_simple\.py" > /dev/null 2>&1; then
    PIDS=$(pgrep -f "python3?.*bot_simple\.py" 2>/dev/null | tr '\n' ' ')
    echo "Bot rodando (PID: $PIDS)"
    exit 0
fi

# 3) Nenhum processo encontrado pelo padrão - listar qualquer coisa com "bot_simple" (diagnóstico)
FOUND=$(pgrep -af "bot_simple" 2>/dev/null | grep -v "pgrep\|grep\|status\.sh" || true)
if [ -n "$FOUND" ]; then
    echo "Processo(s) com 'bot_simple' (comando diferente do esperado):"
    echo "$FOUND"
    echo ""
    echo "Para encerrar: kill \$(pgrep -f 'bot_simple') ou pkill -f 'bot_simple'"
    exit 0
fi

echo "Bot não está rodando (neste computador)."
echo "Se o bot ainda responde no Telegram, pode estar rodando em outro terminal, outro PC ou como serviço."
exit 0
