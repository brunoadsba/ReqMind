# 📚 Guia Completo de Funcionalidades

> **📊 Status de Testes (2026-01-31):** 7/7 funcionalidades core testadas via terminal ✅
> 
> Funcionalidades verificadas: Web Search, RAG Search, Save Memory, Search Code, Filesystem (R/W/List), Git (Status/Diff), Tool Registry
> 
> Ver [Testes e Validação](#testes-e-validação) para detalhes.

## Índice

1. [Chat Inteligente](#1-chat-inteligente)
2. [Análise de Imagens](#2-análise-de-imagens)
3. [Análise de Vídeos](#3-análise-de-vídeos)
4. [Transcrição de Áudio](#4-transcrição-de-áudio)
5. [Text-to-Speech](#5-text-to-speech)
6. [Análise de Documentos](#6-análise-de-documentos)
7. [Ferramentas de Desenvolvimento](#7-ferramentas-de-desenvolvimento)
8. [Web Search](#8-web-search)
9. [Memória Persistente (RAG)](#9-memória-persistente-rag)
10. [Sistema de Lembretes](#10-sistema-de-lembretes)
11. [Ferramentas Extras](#11-ferramentas-extras)
12. [Segurança e Estabilidade (NOVO)](#12-segurança-e-estabilidade-novo)
13. [Comandos do Bot](#13-comandos-do-bot)
14. [Testes e Validação](#14-testes-e-validação)

1. [Chat Inteligente](#1-chat-inteligente)
2. [Análise de Imagens](#2-análise-de-imagens)
3. [Análise de Vídeos](#3-análise-de-vídeos)
4. [Transcrição de Áudio](#4-transcrição-de-áudio)
5. [Text-to-Speech](#5-text-to-speech)
6. [Análise de Documentos](#6-análise-de-documentos)
7. [Ferramentas de Desenvolvimento](#7-ferramentas-de-desenvolvimento)
8. [Web Search](#8-web-search)
9. [Memória Persistente (RAG)](#9-memória-persistente-rag)
10. [Sistema de Lembretes](#10-sistema-de-lembretes)
11. [Ferramentas Extras](#11-ferramentas-extras)
12. [Segurança e Estabilidade (NOVO)](#12-segurança-e-estabilidade-novo)
13. [Comandos do Bot](#13-comandos-do-bot)

---

## 1. Chat Inteligente

### Descrição
Conversação natural com IA usando Groq Llama 3.3 70B, com capacidade de usar ferramentas automaticamente. Quando o Groq retorna limite de uso (429), o bot tenta **Kimi K2.5** via API NVIDIA (requer `NVIDIA_API_KEY` no `.env`); se não houver chave ou o Kimi falhar, responde a partir da **memória RAG** (ex.: NR-29), com truncamento em fronteira de frase e aviso "(Resumo truncado.)". Perguntas que pedem apenas data/hora são respondidas direto, sem chamar o agente.

### Como Usar
Simplesmente envie uma mensagem de texto no Telegram.

### Exemplos

**Conversa Simples:**
```
Você: Olá! Como você está?
Bot: Olá! Estou funcionando perfeitamente e pronto para ajudar. Como posso auxiliar você hoje?
```

**Com Tool Calling Automático:**
```
Você: Qual o clima em São Paulo?
Bot: [usa tool: get_weather("São Paulo")]
     Em São Paulo está 25°C, ensolarado, com umidade de 60%.
```

```
Você: Busque informações sobre Python 3.12
Bot: [usa tool: web_search("Python 3.12")]
     Python 3.12 foi lançado em outubro de 2023 com melhorias...
```

### Capacidades
- ✅ Conversação natural em português
- ✅ Contexto de conversa (histórico)
- ✅ Tool calling automático (15 ferramentas)
- ✅ Raciocínio complexo
- ✅ Múltiplas iterações (até 5)
- ✅ Fallback para Kimi K2.5 (NVIDIA) quando Groq retorna 429 (timeout 20 s)
- ✅ Fallback RAG em 429: se Kimi indisponível, resposta a partir da memória (ex.: NR-29), truncada em fronteira de frase com "(Resumo truncado.)"
- ✅ Resposta direta para perguntas só de data/hora (sem agente)
- ✅ Mensagem de rate limit com tempo estimado (ex.: "em cerca de 6 minutos") quando não há resultado RAG
- ✅ Sanitização de tool call em texto: se o modelo devolver markup de chamada (ex.: save_memory) no conteúdo, o agent remove e executa a ferramenta, evitando vazamento de tokens ao usuário

### Limitações
- ⚠️ Histórico limitado (últimas 10 mensagens)
- ⚠️ Sem memória entre sessões (use save_memory)
- ⚠️ Fallback Kimi K2.5 não usa ferramentas (resposta apenas em texto); timeout de 20 s para falhar rápido se a API não responder

---

## 2. Análise de Imagens

### Descrição
Análise visual de imagens usando Groq Vision (Llama 4 Scout 17B).

### Como Usar
Envie uma foto no Telegram, com ou sem legenda.

### Exemplos

**Análise Simples:**
```
[Envia foto de um gato]
Bot: Esta imagem mostra um gato doméstico de pelagem laranja, 
     deitado em um sofá cinza. O gato parece relaxado e está 
     olhando diretamente para a câmera...
```

**Com Pergunta Específica:**
```
[Envia foto de código]
Caption: "O que este código faz?"
Bot: Este código Python define uma função que calcula o fatorial 
     de um número usando recursão. A função verifica se n é 0 ou 1...
```

**Análise de Documento:**
```
[Envia foto de nota fiscal]
Caption: "Extraia os valores desta nota"
Bot: Identifico os seguintes valores:
     • Subtotal: R$ 150,00
     • Desconto: R$ 15,00
     • Total: R$ 135,00
```

### Capacidades
- ✅ Descrição detalhada de imagens
- ✅ Reconhecimento de objetos, pessoas, texto
- ✅ Análise de código em screenshots
- ✅ Leitura de documentos fotografados
- ✅ Identificação de cores, formas, contexto

### Limitações
- ⚠️ Tamanho máximo: 20MB
- ⚠️ Formatos: JPG, PNG, WebP
- ⚠️ Qualidade da análise depende da qualidade da imagem

---

## 3. Análise de Vídeos

### 3.1 Vídeos do Telegram

### Descrição
Análise completa de vídeos enviados diretamente no Telegram, com análise visual e transcrição de áudio.

### Como Usar
Envie um vídeo no Telegram.

### Exemplo
```
[Envia vídeo de 30 segundos]
Bot: 🎬 Vídeo analisado:

📸 O vídeo mostra uma pessoa explicando conceitos de programação 
    em frente a um quadro branco. Há diagramas de fluxo e código 
    Python escrito no quadro...

🎤 Áudio: "Hoje vamos aprender sobre funções recursivas em Python. 
          Uma função recursiva é aquela que chama a si mesma..."
```

### Capacidades
- ✅ Extração de frame representativo
- ✅ Análise visual com Groq Vision
- ✅ Transcrição de áudio com Whisper
- ✅ Resposta combinada (visual + áudio)

### Limitações
- ⚠️ Tamanho máximo: 50MB (limite do Telegram)
- ⚠️ Duração recomendada: < 5 minutos
- ⚠️ Apenas 1 frame analisado

---

### 3.2 Vídeos do YouTube

### Descrição
Análise de vídeos do YouTube com download, extração de múltiplos frames e análise visual.

### Como Usar
Envie um link do YouTube no Telegram.

### Exemplos

**Análise Automática:**
```
Você: https://youtube.com/watch?v=dQw4w9WgXcQ
Bot: 🎬 Analisando vídeo do YouTube... Isso pode levar alguns minutos.

     🎬 Resumo do Vídeo:
     
     Este vídeo musical mostra um cantor performando em diferentes 
     cenários. No início, ele está em um ambiente interno escuro. 
     No meio do vídeo, há cenas de dança com outras pessoas. 
     No final, o cantor aparece em close-up cantando diretamente 
     para a câmera...
```

**Com Pergunta Específica:**
```
Você: Analise este vídeo e me diga quais são os pontos principais:
      https://youtube.com/watch?v=...
Bot: [Análise focada nos pontos principais]
```

### Capacidades
- ✅ Download automático (qualidade baixa para velocidade)
- ✅ Extração de até 10 frames (1 a cada 5 segundos)
- ✅ Análise de 3 frames (início, meio, fim)
- ✅ Resumo detalhado do conteúdo
- ✅ Suporte a vídeos longos

### Limitações
- ⚠️ Tempo de processamento: 30-60 segundos
- ⚠️ Vídeos muito longos (>30min) podem demorar
- ⚠️ Vídeos privados não funcionam
- ⚠️ Sem análise de áudio (apenas visual)

---

## 4. Transcrição de Áudio

### Descrição
Transcrição de áudio/voz para texto usando Groq Whisper Large v3 Turbo.

### Como Usar
Envie um áudio de voz ou arquivo de áudio no Telegram.

### Exemplos

**Mensagem de Voz:**
```
[Envia áudio de voz de 10 segundos]
Bot: 🎤 Você disse:
     "Olá, preciso que você me ajude a criar um script Python 
      para automatizar o envio de emails"
     
     Claro! Vou ajudar você a criar um script para envio de emails...
```

**Arquivo de Áudio:**
```
[Envia arquivo .mp3]
Bot: 🎵 Você disse:
     "Esta é uma gravação de uma reunião onde discutimos..."
     
     [Resposta contextual baseada na transcrição]
```

### Capacidades
- ✅ Transcrição em português e inglês
- ✅ Alta precisão (Whisper Large v3 Turbo)
- ✅ Processamento rápido (< 10 segundos)
- ✅ Suporte a múltiplos formatos (OGG, MP3, WAV, M4A)
- ✅ Resposta contextual automática

### Limitações
- ⚠️ Tamanho máximo: 20MB
- ⚠️ Qualidade depende do áudio original
- ⚠️ Ruído de fundo pode afetar precisão

---

## 5. Text-to-Speech

### Descrição
Conversão de texto em áudio usando ElevenLabs com voz masculina em português.

### Como Usar
Adicione palavras-chave na sua mensagem: "em áudio", "com áudio", "responda em áudio", "fale", "voz".

### Exemplos

**Resposta em Áudio:**
```
Você: Me explique o que é Python em áudio
Bot: [Resposta em texto]
     [Envia mensagem de voz com a mesma resposta]
```

```
Você: Fale sobre inteligência artificial
Bot: [Resposta em texto + áudio]
```

### Capacidades
- ✅ Voz masculina natural (Antoni)
- ✅ Português brasileiro
- ✅ Entonação e pausas naturais
- ✅ Resposta dupla (texto + áudio)

### Limitações
- ⚠️ Requer API key do ElevenLabs (opcional)
- ⚠️ Limite de caracteres por mês (plano free)
- ⚠️ Tempo de geração: 3-5 segundos

---

## 6. Análise de Documentos

### 6.1 Excel e CSV

### Descrição
Análise profissional de planilhas com estatísticas, insights e recomendações.

### Como Usar
Envie um arquivo .xlsx, .xls ou .csv no Telegram.

### Exemplo

```
[Envia planilha de vendas.xlsx]
Bot: 📊 ANÁLISE DE PLANILHA EXCEL

📁 Arquivo: vendas.xlsx
📐 Dimensões: 150 linhas × 8 colunas

📋 ESTRUTURA:
• Colunas numéricas: Valor, Quantidade, Desconto
• Colunas de texto: Produto, Cliente, Vendedor
• Colunas de data: Data_Venda

📊 AMOSTRA DOS DADOS (primeiras 8 linhas):
[Tabela formatada]

📈 ESTATÍSTICAS (colunas numéricas):
[Estatísticas descritivas]

---

📊 Analisando planilha com IA...

📋 Resumo Executivo:
Esta planilha contém dados de vendas de 150 transações...

🎯 Principais Insights:
1. O produto mais vendido é X com 45 unidades
2. O vendedor com melhor performance é Y
3. Há uma tendência de crescimento nas vendas...

📊 Análise dos Dados:
[Análise detalhada]

💡 Recomendações:
1. Focar em produtos de alta margem
2. Treinar equipe em técnicas de upsell
3. Implementar programa de fidelidade
```

### Capacidades
- ✅ Leitura de Excel (.xlsx, .xls) e CSV
- ✅ Limpeza automática de dados
- ✅ Identificação de tipos de colunas
- ✅ Estatísticas descritivas
- ✅ Análise de valores únicos
- ✅ Insights gerados por IA
- ✅ Recomendações práticas

### Limitações
- ⚠️ Tamanho máximo: 10MB
- ⚠️ Máximo 1000 linhas para análise completa
- ⚠️ Planilhas com múltiplas abas: apenas primeira aba

---

### 6.2 Word (.docx)

### Descrição
Extração de texto de documentos Word.

### Como Usar
Envie um arquivo .docx no Telegram.

### Exemplo
```
[Envia documento.docx]
Bot: 📄 Arquivo Word: documento.docx

Parágrafos: 25

Conteúdo:
[Primeiros 3500 caracteres do documento]
```

### Capacidades
- ✅ Extração de texto completo
- ✅ Preservação de parágrafos
- ✅ Preview automático

### Limitações
- ⚠️ Não extrai imagens
- ⚠️ Não preserva formatação
- ⚠️ Tabelas são convertidas em texto simples

---

### 6.3 Markdown

### Descrição
Leitura de arquivos Markdown.

### Como Usar
Envie um arquivo .md no Telegram.

### Exemplo
```
[Envia README.md]
Bot: 📝 Arquivo Markdown: README.md

Tamanho: 5432 caracteres

Conteúdo:
[Conteúdo do arquivo]
```

---

### 6.4 OCR (Extração de Texto de Imagens)

### Descrição
Extração de texto de imagens usando Tesseract OCR.

### Como Usar
Envie uma imagem como documento (não como foto).

### Exemplo
```
[Envia screenshot de código como documento]
Bot: 📄 Texto extraído (OCR):

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Capacidades
- ✅ Reconhecimento em português e inglês
- ✅ Suporte a múltiplos formatos
- ✅ Extração de código, texto, números

### Limitações
- ⚠️ Qualidade depende da imagem
- ⚠️ Texto manuscrito tem baixa precisão
- ⚠️ Imagens com muito ruído podem falhar

---

## 7. Ferramentas de Desenvolvimento

### 7.1 Busca em Código

### Descrição
Busca por termos em arquivos de código.

### Como Usar
```
Você: Busque "def main" no código
Bot: [usa tool: search_code("def main")]
```

### Exemplo
```
Você: Procure por "async def" nos arquivos Python
Bot: Encontrei 15 ocorrências:
     
     bot_simple.py:86: async def start(update: Update...
     bot_simple.py:115: async def handle_message(update...
     workspace/core/agent.py:45: async def run(self...
```

### Capacidades
- ✅ Busca recursiva em diretórios
- ✅ Filtro por extensões (.py, .js, .ts, etc)
- ✅ Exibe linha e contexto

---

### 7.2 Git Status

### Descrição
Mostra status do repositório Git.

### Como Usar
```
Você: Qual o status do Git?
Bot: [usa tool: git_status()]
```

### Exemplo
```
Você: Mostre o status do repositório
Bot: On branch main
     Your branch is up to date with 'origin/main'.
     
     Changes not staged for commit:
       modified:   bot_simple.py
       modified:   README.md
```

---

### 7.3 Git Diff

### Descrição
Mostra diferenças não commitadas.

### Como Usar
```
Você: Mostre as mudanças no código
Bot: [usa tool: git_diff()]
```

### Exemplo
```
Você: Quais arquivos foram modificados?
Bot: diff --git a/bot_simple.py b/bot_simple.py
     index 1234567..abcdefg 100644
     --- a/bot_simple.py
     +++ b/bot_simple.py
     @@ -115,6 +115,7 @@
     +    # Nova funcionalidade
```

---

### 7.4 Filesystem

#### read_file
```
Você: Leia o arquivo config.json
Bot: [usa tool: read_file("config.json")]
     {
       "name": "Assistente Digital",
       "version": "1.0.0"
     }
```

#### write_file
```
Você: Crie um arquivo teste.txt com "Hello World"
Bot: [usa tool: write_file("teste.txt", "Hello World")]
     ✅ Arquivo salvo em teste.txt
```

#### list_directory
```
Você: Liste os arquivos do diretório workspace
Bot: [usa tool: list_directory("workspace")]
     Diretório: workspace/
     
     Arquivos:
     • bot_simple.py
     • README.md
     
     Diretórios:
     • core/
     • tools/
```

---

## 8. Web Search

### Descrição
Busca informações na web usando DuckDuckGo.

### Como Usar
```
Você: Busque na web sobre Python 3.12
Bot: [usa tool: web_search("Python 3.12")]
```

### Exemplo
```
Você: Pesquise sobre inteligência artificial
Bot: Encontrei os seguintes resultados:

1. **O que é Inteligência Artificial?**
   Inteligência artificial é a capacidade de máquinas...
   Fonte: wikipedia.org

2. **IA no Brasil**
   O mercado de IA no Brasil cresceu 40% em 2023...
   Fonte: exame.com

3. **Aplicações de IA**
   As principais aplicações incluem...
   Fonte: mit.edu
```

### Capacidades
- ✅ Busca em tempo real
- ✅ Resultados relevantes
- ✅ Múltiplas fontes
- ✅ Sem rastreamento (DuckDuckGo)

### Limitações
- ⚠️ Máximo 5 resultados por busca
- ⚠️ Sem acesso a conteúdo pago
- ⚠️ Resultados podem variar

---

## 9. Memória Persistente (RAG)

### 9.1 Salvar Informação

### Descrição
Salva informações importantes na memória de longo prazo.

### Como Usar
```
Você: Salve na memória: meu aniversário é dia 15 de março
Bot: [usa tool: save_memory("aniversário é dia 15 de março")]
     ✅ Informação salva na memória
```

### Exemplo
```
Você: Lembre-se: meu projeto principal é o Assistente Digital
Bot: ✅ Informação salva. Vou lembrar disso!
```

---

### 9.2 Buscar na Memória

### Descrição
Busca informações salvas anteriormente.

### Como Usar
```
Você: Quando é meu aniversário?
Bot: [usa tool: rag_search("aniversário")]
     Seu aniversário é dia 15 de março.
```

### Exemplo
```
Você: Qual é meu projeto principal?
Bot: [busca na memória]
     Seu projeto principal é o Assistente Digital.
```

### Capacidades
- ✅ Busca por substring na memória (`memory.json` em `src/dados/`)
- ✅ Memória persistente entre sessões
- ✅ Contexto de longo prazo

### 9.3 Alimentação de normas (ex.: NR-29)

A memória RAG pode ser alimentada com textos longos (ex.: resumo ou texto oficial da NR-29) para que o bot responda mesmo quando a API está em rate limit (429).

**Scripts**
- `scripts/feed_nr29_to_memory.py` — injeta resumo estruturado da NR-29 na memória.
- `scripts/feed_nr29_oficial.py` — lê `scripts/nr29_oficial_dou.txt`, divide por seções (29.1, 29.2, …) e injeta o texto oficial na memória.

**Uso**
```bash
PYTHONPATH=src python scripts/feed_nr29_to_memory.py
PYTHONPATH=src python scripts/feed_nr29_oficial.py [caminho_opcional.txt]
```

**Fallback em 429:** Se a API Groq retornar 429 e o Kimi (NVIDIA) não estiver disponível, o agente busca na memória por termos como "NR-29" ou "NR" e devolve o trecho encontrado (até ~1200 caracteres), truncando em fronteira de frase e adicionando "(Resumo truncado.)".

---

## 10. Sistema de Lembretes

### Descrição
Cria lembretes que são enviados por Email e Telegram no horário especificado.

### Como Usar
```
Você: Crie um lembrete para reunião amanhã às 15h
Bot: [usa tool: create_reminder("reunião", "31/01/2026 15:00")]
     ✅ Lembrete criado! Você receberá notificação por email e Telegram.
```

### Exemplos

**Lembrete Simples:**
```
Você: Me lembre de ligar para o cliente às 14h
Bot: ✅ Lembrete criado para hoje às 14:00
```

**Lembrete com Data:**
```
Você: Lembre-me de pagar a conta dia 05/02 às 10h
Bot: ✅ Lembrete criado para 05/02/2026 às 10:00
```

### Notificação Recebida
```
📧 Email:
Assunto: 🔔 Lembrete: Reunião
Corpo: Este é seu lembrete agendado:
       📝 Reunião
       🕐 Horário: 31/01/2026 15:00

💬 Telegram:
🔔 LEMBRETE

📝 Reunião
🕐 31/01/2026 15:00
```

### Capacidades
- ✅ Notificação dupla (Email + Telegram)
- ✅ Múltiplos formatos de data
- ✅ Monitoramento automático
- ✅ Precisão de ±1 minuto

### Limitações
- ⚠️ Requer configuração de Email (SMTP)
- ⚠️ Lembretes são perdidos se o bot reiniciar
- ⚠️ Armazenamento em arquivo JSON temporário

---

## 11. Ferramentas Extras

### 11.1 Clima

### Descrição
Obtém informações de clima atual usando OpenWeatherMap.

### Como Usar
```
Você: Qual o clima em São Paulo?
Bot: [usa tool: get_weather("São Paulo")]
```

### Exemplo
```
Você: Como está o tempo no Rio de Janeiro?
Bot: 🌤️ Clima no Rio de Janeiro:
     
     🌡️ Temperatura: 28°C
     🤚 Sensação: 30°C
     ☁️ Condição: Parcialmente nublado
     💧 Umidade: 75%
     💨 Vento: 3.5 m/s
```

### Capacidades
- ✅ Clima em tempo real
- ✅ Qualquer cidade do mundo
- ✅ Informações detalhadas

### Limitações
- ⚠️ Requer API key (opcional)
- ⚠️ Limite de requisições (plano free)

---

### 11.2 Notícias

### Descrição
Busca últimas notícias sobre um tópico usando NewsAPI.

### Como Usar
```
Você: Busque notícias sobre tecnologia
Bot: [usa tool: get_news("tecnologia")]
```

### Exemplo
```
Você: Quais as últimas notícias sobre IA?
Bot: 📰 Últimas notícias sobre IA:

1. **OpenAI lança novo modelo GPT-5**
   Fonte: TechCrunch
   Data: 30/01/2026
   Link: [url]

2. **Brasil investe R$ 1 bilhão em IA**
   Fonte: Folha de S.Paulo
   Data: 29/01/2026
   Link: [url]
```

### Limitações
- ⚠️ Requer API key (opcional)
- ⚠️ Máximo 5 notícias por busca

---

### 11.3 Gráficos

### Descrição
Gera gráficos usando matplotlib.

### Como Usar
```
Você: Crie um gráfico de barras com vendas: Jan=100, Fev=150, Mar=120
Bot: [usa tool: create_chart(...)]
     [Envia imagem do gráfico]
```

### Tipos Suportados
- Barras
- Linhas
- Pizza
- Dispersão

---

### 11.4 Geração de Imagens

### Descrição
Gera imagens usando IA (se configurado).

### Como Usar
```
Você: Gere uma imagem de um gato astronauta
Bot: [usa tool: generate_image("gato astronauta")]
```

### Limitações
- ⚠️ Requer API key de serviço de geração
- ⚠️ Não implementado por padrão

---

## 12. Segurança e Estabilidade (NOVO)

### 12.1 SecureFileManager

**Descrição**
Gerenciamento seguro de arquivos temporários com auto-cleanup garantido.

**Como Funciona**
- Cria arquivos temporários em diretório seguro (`/tmp/moltbot_secure`)
- Sanitiza filenames contra path traversal
- Valida MIME types reais usando python-magic
- Garante deleção automática (mesmo em caso de erro)

**Exemplo no Bot**
```
Quando você envia um vídeo:
    ↓
Sistema cria arquivo temporário seguro
    ↓
Processa vídeo (extrai frame, áudio)
    ↓
Arquivo automaticamente deletado após processamento
```

**Benefícios**
- ✅ Zero arquivos temporários residuais
- ✅ Proteção contra path traversal
- ✅ Validação real de tipos de arquivo
- ✅ Limpeza automática garantida

---

### 12.2 SafeSubprocessExecutor

**Descrição**
Execução assíncrona e segura de subprocessos (ffmpeg, etc).

**Como Funciona**
- Whitelist de comandos permitidos
- Bloqueio de command injection (`,`, `&&`, `||`, etc)
- Timeout de 30 segundos
- Execução assíncrona (não bloqueia o bot)

**Exemplo no Bot**
```
Para extrair frame de vídeo:
    ↓
Sistema executa ffmpeg de forma segura
    ↓
Timeout automático se travar
    ↓
Retorna resultado ou erro
```

**Comandos Permitidos**
- `ffmpeg` - Processamento de vídeo/áudio
- `ffprobe` - Análise de mídia
- `tesseract` - OCR
- `python`, `python3` - Scripts Python

**Segurança**
- ✅ Previne command injection
- ✅ Timeout evita processos travados
- ✅ Não bloqueia o bot
- ✅ Tratamento especial para exit codes

---

### 12.3 Retry com Backoff

**Descrição**
Tentativas automáticas em caso de falha de API.

**Como Funciona**
- Se API falhar, tenta novamente automaticamente
- Espera 1s → 2s → 4s entre tentativas (exponential backoff)
- Máximo de 3 tentativas por padrão

**Exemplo**
```
Análise de imagem:
    ↓
API Groq falha (timeout)
    ↓
Sistema aguarda 1 segundo
    ↓
Tenta novamente (tentativa 2/3)
    ↓
Sucesso!
```

**Benefícios**
- ✅ Resiliência a falhas temporárias
- ✅ Melhor experiência do usuário
- ✅ Menos erros por instabilidade de rede

---

### 12.4 Rate Limiting

**Descrição**
Proteção contra abuso do sistema.

**Limites**
- 20 mensagens por minuto (texto)
- 5 mídias por minuto (fotos, vídeos, áudio)
- 3 análises YouTube por 5 minutos

**Quando Atinge o Limite**
```
Você: [envia 21 mensagens em 1 minuto]
Bot: ⏱️ Muitas requisições. Aguarde um momento.
     Requisições restantes: 0
```

**Rate limit da API (429)**  
Quando o Groq retorna 429: (1) tenta Kimi K2.5 (NVIDIA); (2) se não houver chave ou Kimi falhar, tenta responder a partir da memória RAG (ex.: NR-29), com truncamento em fronteira de frase; (3) caso não haja resultado na memória, devolve mensagem com tempo estimado (ex.: "Tente novamente em cerca de 6 minutos").

**Benefícios**
- ✅ Previne spam
- ✅ Uso justo entre usuários
- ✅ Protege recursos do servidor

---

### 12.5 Configuração Centralizada

**Descrição**
Todas as configurações em um único lugar.

**Como Funciona**
- Configurações via variáveis de ambiente
- Defaults sensíveis
- Fácil acesso global

**Exemplo**
```python
from config import config

# Paths
config.BASE_DIR       # Diretório base
config.TEMP_DIR       # Diretório temporário

# Modelos
config.GROQ_MODEL_VISION  # Modelo de visão
config.GROQ_MODEL_CHAT    # Modelo de chat

# Limites
config.MAX_FILE_SIZE_MB   # 50MB
config.REQUEST_TIMEOUT    # 30s
```

**Variáveis de Ambiente**
```bash
MOLTBOT_DIR=...           # Diretório base
MOLTBOT_TEMP=...          # Diretório temporário
ALLOWED_USERS=...         # IDs autorizados (123,456)
```

**Benefícios**
- ✅ Sem hardcoded paths
- ✅ Fácil deploy em diferentes ambientes
- ✅ Manutenção simplificada

---

### 12.6 Asyncio Puro

**Descrição**
Sistema de lembretes modernizado para melhor estabilidade.

**Mudança**
- Antes: Threading (problemático)
- Depois: Asyncio.create_task() (moderno)

**Benefícios**
- ✅ Melhor integração com asyncio
- ✅ Graceful shutdown (limpa recursos)
- ✅ Menos problemas de concorrência

---

## 13. Comandos do Bot

### /start
Inicia o bot e mostra mensagem de boas-vindas.

```
/start

Bot: 🤖 Moltbot ativo!

Sou seu assistente pessoal com acesso a:
• Busca na web
• Memória persistente
• Operações de arquivo
• Git

Como posso ajudar?
```

---

### /clear
Limpa o histórico de conversação.

```
/clear

Bot: ✅ Histórico limpo!
```

---

### /status
Mostra status do sistema e ferramentas disponíveis.

```
/status

Bot: 🟢 Sistema operacional

Ferramentas disponíveis: 15
• web_search, rag_search, save_memory, search_code, 
  read_file, write_file, list_directory, git_status, 
  git_diff, get_weather, get_news, create_reminder, 
  create_chart, generate_image
```

---

## Dicas de Uso

### 1. Seja Específico
```
❌ "Analise isso"
✅ "Analise esta imagem e me diga quais objetos você identifica"
```

### 2. Use Contexto
```
✅ "Baseado na planilha que enviei, qual produto tem melhor margem?"
```

### 3. Combine Funcionalidades
```
✅ "Busque na web sobre Python async/await e salve na memória"
```

### 4. Peça Formatação
```
✅ "Liste os arquivos em formato de tabela"
✅ "Resuma em 3 pontos principais"
```

### 5. Use Lembretes
```
✅ "Me lembre de revisar o código amanhã às 9h"
```

---

## 14. Testes e Validação

### Status de Testes (2026-01-31)

✅ **7/7 funcionalidades core testadas via terminal (100%)**

Testes executados em ambiente de produção (venv311) verificando operações reais:

| # | Funcionalidade | Status | Evidência |
|---|---------------|--------|-----------|
| 1 | **Web Search (DuckDuckGo)** | ✅ OK | Busca executada com sucesso |
| 2 | **RAG Search (Memória)** | ✅ OK | Encontrou entradas na memória |
| 3 | **Save Memory** | ✅ OK | Salvou informação de teste |
| 4 | **Search Code** | ✅ OK | 88 matches de "async def" |
| 5 | **Filesystem (R/W/List)** | ✅ OK | Todas operações OK |
| 6 | **Git (Status/Diff)** | ✅ OK | Status e diff operacionais |
| 7 | **Tool Registry** | ✅ OK | 8 ferramentas registradas |

### Como Executar os Testes

```bash
# Teste completo (7 funcionalidades)
cd /home/brunoadsba/clawd/moltbot-setup
source venv311/bin/activate
python3 /home/brunoadsba/Assistente-Digital/assistente/tests/test_bot_completo.py

# Teste simplificado (4 funcionalidades - core)
python3 /home/brunoadsba/Assistente-Digital/assistente/tests/test_bot_simples.py
```

### Arquivos de Teste

```
tests/
├── test_bot_completo.py         # 7 funcionalidades ✅
├── test_bot_simples.py          # 4 funcionalidades
├── test_bot_funcionalidades.py  # 11 funcionalidades
├── test_e2e.py                  # Testes E2E originais
└── test_e2e_simple.py           # Testes E2E simplificados
```

---

## Troubleshooting

### Bot não responde
- Verifique se está autorizado (user_id na whitelist)
- Veja os logs: `tail -f bot.log`

### Erro em análise de vídeo
- Vídeo muito grande? Tente um menor
- Link do YouTube inválido? Verifique o URL

### Transcrição incorreta
- Áudio com muito ruído? Grave em ambiente silencioso
- Idioma não suportado? Use português ou inglês

### Ferramenta não funciona
- API key configurada? Verifique `.env`
- Limite de requisições? Aguarde ou upgrade do plano

---

## Conclusão

O Assistente Digital oferece um conjunto abrangente de funcionalidades para produtividade, análise de dados e automação. Explore as diferentes capacidades e combine-as para criar workflows poderosos!

**Precisa de ajuda?** Consulte `ARCHITECTURE.md` para detalhes técnicos ou `DEVELOPMENT.md` para adicionar novas funcionalidades.
