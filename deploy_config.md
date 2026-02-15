# 🔄 Garantindo que o Bot esteja Sempre Ligado

Para que os lembretes e as notícias das 7h sejam confiáveis, o bot precisa reiniciar automaticamente se o servidor cair ou o processo falhar.

---

## 1. Docker (Recomendado)

### Usando docker-compose.yml

Adicione a política de restart no seu `docker-compose.yml`:

```yaml
version: '3.8'

services:
  assistente-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: assistente-bot
    restart: unless-stopped  # Garante que o container suba com o Docker
    env_file:
      - .env
    volumes:
      - ./dados:/app/dados
      - ./data:/app/data
      - ./tmp:/app/tmp
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app/src
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Usando docker run diretamente

```bash
docker run -d \
  --name assistente-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/dados:/app/dados \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/tmp:/app/tmp \
  assistente-bot:latest
```

**Políticas de restart disponíveis:**
- `no` - Nunca reinicia (padrão)
- `on-failure` - Reinicia apenas se o container sair com código de erro
- `always` - Sempre reinicia, independente do código de saída
- `unless-stopped` - Sempre reinicia, exceto se o container for parado manualmente

> 💡 **Recomendado:** `unless-stopped` - permite parar o container manualmente sem que ele reinicie automaticamente.

---

## 2. Systemd (Se rodar fora do Docker)

Crie um arquivo em `/etc/systemd/system/assistente-bot.service`:

```ini
[Unit]
Description=Assistente Bot Service
After=network.target

[Service]
Type=simple
User=brunoadsba
WorkingDirectory=/home/brunoadsba/ReqMind/assistente
Environment=PYTHONPATH=/home/brunoadsba/ReqMind/assistente/src
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/brunoadsba/ReqMind/assistente/venv/bin/python -m src.bot_simple
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Comandos úteis:

```bash
# Recarregar configurações do systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable assistente-bot

# Iniciar o serviço agora
sudo systemctl start assistente-bot

# Verificar status
sudo systemctl status assistente-bot

# Ver logs
sudo journalctl -u assistente-bot -f

# Parar o serviço
sudo systemctl stop assistente-bot
```

---

## 3. Health Check (Opcional)

Para monitorar se o bot está "vivo", você pode adicionar um healthcheck no Docker:

```yaml
services:
  assistente-bot:
    # ... configuração existente ...
    healthcheck:
      test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/bot.pid') else 1)"]
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 30s
```

Ou usando curl se o bot expuser um endpoint de health:

```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 1m
      timeout: 10s
      retries: 3
```

---

## 4. Verificação de Status

### Comandos para verificar se o bot está rodando:

```bash
# Verificar se o container está rodando (Docker)
docker ps | grep assistente-bot

# Verificar logs do container
docker logs assistente-bot --tail 50

# Verificar se o serviço está ativo (Systemd)
sudo systemctl is-active assistente-bot

# Verificar processo do bot (se rodar sem Docker)
ps aux | grep bot_simple
```

### Script de monitoramento simples:

Crie um arquivo `check_bot.sh`:

```bash
#!/bin/bash

# Verifica se o bot está rodando
if ! docker ps | grep -q assistente-bot; then
    echo "⚠️ Bot não está rodando! Iniciando..."
    cd /home/brunoadsba/ReqMind/assistente
    make start-docker
    echo "✅ Bot reiniciado em $(date)" >> /tmp/bot_restarts.log
fi
```

Adicione ao crontab para verificar a cada 5 minutos:

```bash
*/5 * * * * /home/brunoadsba/ReqMind/assistente/check_bot.sh
```

---

## 5. Checklist de Deploy

- [ ] Arquivo `.env` configurado corretamente (sem aspas)
- [ ] Docker instalado e configurado
- [ ] `docker-compose.yml` com `restart: unless-stopped`
- [ ] Volumes mapeados corretamente (`dados/`, `data/`, `tmp/`)
- [ ] Portas expostas (se necessário)
- [ ] Logs configurados com rotação
- [ ] Script de health check (opcional)
- [ ] Monitoramento configurado (opcional)

---

## 6. Troubleshooting

### Container reinicia em loop

```bash
# Verificar logs
docker logs assistente-bot --tail 100

# Verificar se .env está correto
docker exec assistente-bot env | grep -E 'TELEGRAM|GROQ'

# Verificar permissões
docker exec assistente-bot ls -la /app/dados
```

### Bot não inicia no boot

```bash
# Verificar status do Docker
sudo systemctl status docker

# Verificar se o container tem restart policy
docker inspect assistente-bot | grep -A 5 RestartPolicy

# Verificar logs do systemd (se usar systemd)
sudo journalctl -u docker.service
```

### Erro de permissão em volumes

```bash
# Corrigir permissões
sudo chown -R 1000:1000 /home/brunoadsba/ReqMind/assistente/dados
sudo chown -R 1000:1000 /home/brunoadsba/ReqMind/assistente/data
sudo chown -R 1000:1000 /home/brunoadsba/ReqMind/assistente/tmp
```

---

**Última atualização:** 2026-02-06  
**Versão:** 1.0
