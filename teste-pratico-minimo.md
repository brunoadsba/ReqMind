# Teste prático mínimo (5–6 prompts)

Versão enxuta do [teste-pratico.md](teste-pratico.md) para validar o essencial **sem estourar o limite da API Groq** em uma única sessão.

Recomendação: executar na ordem abaixo, com pausa de ~30 s entre cada prompt.

---

1. **Chat + contexto do usuário**  
   `O que você sabe sobre mim como usuário deste bot?`

2. **Busca na web**  
   `Busque na web as novidades do Python 3.12 e me traga um resumo em 3 tópicos.`

3. **Memória – salvar**  
   `Salve na memória que eu prefiro respostas diretas, em português brasileiro, e com foco em código.`

4. **Memória – resgatar**  
   `O que você tem salvo na memória sobre minhas preferências?`

5. **Arquivos – listar diretório do projeto**  
   `Liste os arquivos do diretório atual do projeto e destaque os principais de documentação.`

6. **Arquivos – ler** (opcional; consome mais tokens)  
   `Leia o conteúdo do arquivo MEMORY.md e resuma em até 5 linhas.`

---

Se o limite for atingido antes do fim, aguarde o tempo indicado na mensagem do bot e retome ou use o [teste prático completo](teste-pratico.md) em blocos separados.
