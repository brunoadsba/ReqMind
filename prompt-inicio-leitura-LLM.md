
Você é uma LLM conectada ao repositório do projeto "Assistente Digital" (bot Telegram com IA).

Sua PRIMEIRA tarefa é ler e entender a documentação, sem sugerir mudanças de código nem editar arquivos, apenas construindo um modelo mental do sistema.

Siga EXATAMENTE esta ordem de leitura:

1. Leia `MEMORY.md`
2. Leia `docs/ARCHITECTURE.md`
3. Leia `docs/TOOLS_REFERENCE.md`
4. Leia `docs/DEVELOPMENT.md`
5. Leia `README.md`

Para cada documento lido:

1. Faça um resumo em no máximo 5 bullets, focando em:
   - Papel do documento no projeto
   - Principais decisões e responsabilidades descritas
   - Riscos ou pontos de atenção relevantes
2. Extraia e anote:
   - Componentes principais citados (arquivos, módulos, serviços)
   - Convenções e padrões (segurança, testes, tool calling, estilo)
   - Dependências externas importantes (APIs, modelos, serviços)

Ao final de todos os documentos:

1. Monte um modelo mental único do projeto, cobrindo:
   - Fluxo principal: Telegram → bot → agent → tools → serviços externos
   - Como segurança, RAG, mídia e testes se encaixam
2. Liste, em até 10 bullets, o que você considera:
   - (a) o "contrato" do sistema (o que ele promete fazer)
   - (b) restrições importantes (limites de API, segurança v1.1, uso pessoal, storage local etc.)
3. Não proponha refactors nem novas features nesta fase. O objetivo agora é apenas ENTENDER o projeto.

Quando terminar, responda apenas com:
1. Resumo por documento
2. Modelo mental único do projeto
3. Lista de contratos e restrições


