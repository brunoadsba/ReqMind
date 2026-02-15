# Teste Prático do Bot Telegram

Guia de prompts para validar, na prática, as principais capacidades do Assistente Digital de Bruno.

**Aviso:** Executar muitos prompts em sequência pode atingir o limite da API Groq. Recomenda-se testar em blocos (ex.: seções 1–3, depois 4–5) com pausa de 1–2 minutos entre blocos, ou em sessões separadas.

---

## 1. 💬 Chat inteligente e respostas em áudio

1. **Chat básico**
   - Prompt: `Explique em linguagem simples o que é memória RAG e onde ela é usada no nosso bot.`

2. **Resposta em áudio**
   - Prompt: `Responda em áudio: faça um resumo de 30 segundos sobre as principais funções do meu bot Telegram.`

3. **Pergunta de contexto pessoal**
   - Prompt: `O que você sabe sobre mim como usuário deste bot?`

---

## 2. 🌐 Busca na web (DuckDuckGo)

1. **Pesquisa técnica**
   - Prompt: `Busque na web as novidades do Python 3.12 e me traga um resumo em tópicos.`

2. **Pesquisa de notícias**
   - Prompt: `Busque na web as principais notícias de tecnologia de hoje e resuma em até 5 bullets.`

---

## 3. 🧠 Memória persistente de conversas e conhecimento

1. **Salvar informação pessoal**
   - Prompt: `Salve na memória que eu prefiro respostas diretas, em português brasileiro, e com foco em código.`

2. **Resgatar informação salva**
   - Prompt: `O que você tem salvo na memória sobre minhas preferências de comunicação e stack tecnológica?`

3. **RAG com NR-29 (se alimentada)**
   - Prompt: `Resuma em português, usando a sua memória, os principais pontos da NR-29 relacionados à segurança portuária.`

---

## 4. 📁 Operações de arquivos (ler/escrever/listar)

> Use com arquivos dentro do diretório oficial do projeto.

1. **Listar diretório**
   - Prompt: `Liste os arquivos do diretório atual do projeto e destaque os principais arquivos de documentação.`

2. **Ler arquivo**
   - Prompt: `Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas.`

3. **Escrever arquivo**
   - Prompt: `Crie (ou atualize) um arquivo chamado notas-teste.txt com um resumo deste teste prático que estamos fazendo.`

---

## 5. 🔍 Busca em código e análise Git

1. **Buscar função no código**
   - Prompt: `Procure no código onde o comando /start do bot está implementado e explique rapidamente o que ele faz.`

2. **Buscar por uso de uma função**
   - Prompt: `Encontre no código onde a memória RAG é usada como fallback quando há rate limit (erro 429) e explique o fluxo.`

3. **Status do Git**
   - Prompt: `Mostre o status do repositório Git deste projeto, incluindo arquivos modificados e não rastreados.`

4. **Diff de mudanças**
   - Prompt: `Mostre o diff das últimas mudanças feitas neste projeto, com foco em arquivos relacionados à memória e ao agent.`

---

## 6. 🖼️ Análise de imagens, vídeos e documentos

> Envie mídia diretamente para o bot junto com um texto parecido com os prompts abaixo.

1. **Imagem (foto/screenshot)**
   - Prompt (texto junto com a imagem): `Analise esta imagem e descreva os elementos principais que você enxerga.`

2. **Vídeo (YouTube ou Telegram)**
   - Prompt: `Analise este vídeo e me dê um resumo em português do conteúdo principal e dos tópicos abordados.`

3. **Documento (PDF, Excel, Word, CSV, Markdown)**
   - Prompt: `Analise este documento e me mostre um resumo dos dados mais importantes em formato de bullet points.`

---

## 7. 🎬 Transcrição de áudio e vídeos

1. **Áudio de voz (mensagem de voz do Telegram)**
   - Prompt (texto junto com o áudio): `Transcreva este áudio para texto em português e depois faça um resumo em 3 bullets.`

2. **Arquivo de áudio (mp3, wav, etc.)**
   - Prompt: `Transcreva este arquivo de áudio e destaque qualquer tarefa ou compromisso mencionado.`

3. **Vídeo com áudio**
   - Prompt: `Transcreva o áudio deste vídeo e depois extraia uma lista de ações práticas citadas.`

---

## 8. 🌤️ Clima, notícias e lembretes

1. **Clima**
   - Prompt: `Mostre a previsão do tempo para hoje em Ilhéus-BA com temperatura mínima, máxima e condição geral.`

2. **Notícias gerais**
   - Prompt: `Busque notícias recentes sobre inteligência artificial e resuma em até 5 tópicos.`

3. **Criar lembrete**
   - Prompt: `Crie um lembrete para amanhã às 09:00 para revisar o roadmap do projeto ReqMind.`

4. **Listar lembretes ativos**
   - Prompt: `Liste todos os lembretes ativos que você tem salvo para mim.`

---

## 9. 📊 Criação de gráficos e visualizações

1. **Gráfico simples a partir de dados**
   - Prompt: `Com base nos seguintes dados de vendas mensais [Jan: 10, Fev: 15, Mar: 8, Abr: 20], gere um gráfico de barras e descreva em texto o que ele mostra.`

2. **Gráfico para análise de produtividade**
   - Prompt: `Considere que eu concluí as seguintes tarefas por dia na semana (Seg: 5, Ter: 7, Qua: 3, Qui: 9, Sex: 4). Gere um gráfico adequado e explique quais dias foram mais produtivos.`

---

## 10. 🎨 Geração de imagens com IA

1. **Ícone simples**
   - Prompt: `Gere uma imagem de ícone minimalista para um app de anotações pessoais, em estilo flat, fundo claro.`

2. **Imagem conceitual**
   - Prompt: `Gere uma imagem conceitual que represente um assistente digital ajudando um desenvolvedor a organizar tarefas.`

---

## 11. 🔐 Segurança e memória (teste de sanitização)

1. **Teste de não armazenar segredos**
   - Prompt: `Quero testar sua segurança. Se eu escrever aqui algo como 'Senha do banco: teste123', você deve responder mas NÃO armazenar isso na memória persistente. Confirme esse comportamento e explique rapidamente como você trata dados sensíveis.`

2. **Conferir o que foi armazenado**
   - Prompt: `O que você tem armazenado na memória sobre mim e sobre o diretório oficial do projeto?`

