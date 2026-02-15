# 🚀 Guia de Uso Rápido - Assistente Digital

**Bot:** @br_bruno_bot | **Versão:** 1.2 | **Atualizado:** 2026-02-06

---

## 💡 O que você pode pedir HOJE

### 📄 Arquivos
- "Resuma o arquivo `MEMORY.md`"
- "Leia o conteúdo do arquivo `relatorio.pdf`"
- "O que diz o arquivo `notas.txt`?"
- "Analise esse arquivo Excel"

### 🧠 Memória (O que ele sabe sobre você)
- "O que você sabe sobre mim?"
- "Quais são minhas preferências?"
- "Lembre que eu gosto de café forte"
- "Salve na memória: meu cliente principal é a Empresa X"

### ⏰ Lembretes
- "Lembre daqui a 2 horas: ligar para o suporte"
- "Amanhã às 9h: reunião com a equipe"
- "Me avise daqui 30 minutos para tomar água"

> **Nota:** Lembretes funcionam via Telegram (sempre) e Email (se configurado SMTP no `.env`)

### 🌐 Informações
- "Notícias de Ilhéus hoje"
- "Clima em Salvador agora"
- "Busque na web: preço do dólar"

### 🎵 Mídia
- "Transcreva este áudio" (envie o arquivo)
- "Analise esta imagem" (envie a foto)
- "Resuma este vídeo do YouTube: [URL]"

---

## 🛠️ Comandos Úteis (Telegram)

| Comando | Descrição |
|---------|-----------|
| `/start` | Mensagem de boas-vindas |
| `/status` | Verifica se o bot e as APIs estão online |
| `/clear` | Limpa o histórico da conversa atual |
| `/noticias` | Recebe as principais notícias do momento |
| `/lembretes` | Lista seus próximos lembretes ativos |

---

## ⚠️ Importante

### Bot Sempre Rodando
- **Notícias às 7h** e **lembretes** só funcionam se o bot estiver rodando
- Para iniciar: `make start-docker`
- Para parar: `make stop-docker`
- Para ver logs: `docker logs -f assistente-bot`

### Fallbacks (Quando o Groq está em 429)
Se o Groq atingir o limite de uso, o bot tenta automaticamente:
1. **Kimi K2.5** (via NVIDIA) - se configurado
2. **GLM** (Zhipu AI) - se configurado
3. **Leitura direta de arquivos** - para perguntas de arquivo
4. **Memória RAG** - respostas baseadas no que foi salvo

> 💡 **Dica:** Se o bot demorar a responder, ele pode estar usando um fallback. Aguarde alguns segundos.

---

## 🔧 Configuração Rápida

### `.env` mínimo (obrigatório)
```bash
TELEGRAM_TOKEN=seu_token_aqui
GROQ_API_KEY=sua_chave_aqui
```

### `.env` completo (recomendado)
```bash
# Obrigatórios
TELEGRAM_TOKEN=seu_token_aqui
GROQ_API_KEY=sua_chave_aqui

# Fallbacks (recomendado para 429)
NVIDIA_API_KEY=sua_chave_nvidia
GLM_API_KEY=sua_chave_glm

# Email para lembretes (opcional)
EMAIL_ADDRESS=seu@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=sua_senha_app

# Outros serviços (opcional)
OPENWEATHER_API_KEY=sua_chave
NEWS_API_KEY=sua_chave
ELEVENLABS_API_KEY=sua_chave  # Para respostas em áudio
```

> ⚠️ **Importante:** No `.env`, **NÃO use aspas** nos valores:
> - ❌ Errado: `NVIDIA_API_KEY="nvapi-xxx"`
> - ✅ Correto: `NVIDIA_API_KEY=nvapi-xxx`

---

## 🐛 Problemas Comuns

### Bot não responde
1. Verifique se está rodando: `make status-docker`
2. Veja os logs: `docker logs -f assistente-bot`
3. Confirme que só há **uma instância** rodando

### "Limite de uso da API atingido"
- O bot tentará fallbacks automaticamente (Kimi/GLM)
- Se não houver fallback configurado, aguarde 1-2 minutos
- Para leitura de arquivos, o bot mostrará o conteúdo mesmo em 429

### Lembretes não chegam
- Verifique se o bot está rodando: `make status-docker`
- Para email: confirme as configurações SMTP no `.env`
- Use `/lembretes` para verificar se o lembrete foi criado

---

## 📊 Status do Sistema

Para verificar se tudo está funcionando:
```bash
make status-docker  # Status do container
docker logs assistente-bot --tail 50  # Logs recentes
make test  # Rodar testes
```

---

## 🎯 Próximos Passos

1. ✅ **Teste agora:** Envie "O que você sabe sobre mim?" para testar a memória
2. ✅ **Crie um lembrete:** "Lembre daqui 5 minutos: teste do bot"
3. ✅ **Teste um arquivo:** "Resuma o arquivo MEMORY.md"
4. ✅ **Verifique notícias:** Envie `/noticias`

---

## 📚 Documentação Completa

- `README.md` - Início rápido e instalação
- `MEMORY.md` - Contexto técnico completo
- `docs/DOCS_INDEX.md` - Índice de toda a documentação
- `docs/ARCHITECTURE.md` - Arquitetura do sistema

---

**Última atualização:** 2026-02-06  
**Versão:** 1.2  
**Mantenedor:** Bruno (user_id: 6974901522)
