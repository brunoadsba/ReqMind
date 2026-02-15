# OpenCode + NVIDIA API (Kimi K2.5)

Configuração do OpenCode para usar o modelo `moonshotai/kimi-k2.5` via NVIDIA API.

## Já configurado

- **`~/.config/opencode/opencode.json`**: provider `nvidia-kimi` adicionado (mesclado ao config existente).
- **`.env`** (projeto): variável `NVIDIA_API_KEY=` criada; preencha com sua chave NVIDIA e não commite.

## Pendente (manual)

1. **Preencher a API key**  
   Edite o `.env` e coloque sua chave NVIDIA em `NVIDIA_API_KEY=...` (após revogar a antiga, crie uma nova em [NVIDIA API](https://build.nvidia.com/)).

2. **Carregar o ambiente antes de abrir o OpenCode**  
   No terminal, a partir da raiz do projeto:
   ```bash
   set -a && source .env && set +a && opencode
   ```
   Ou exporte só a chave: `export NVIDIA_API_KEY="sua-chave"`.

3. **No OpenCode**  
   `/connect` → escolha o provider **nvidia-kimi** e informe a key se solicitado. Depois `/models` → selecione **Kimi K2.5 (NVIDIA)**.

## CodeNomad

O CodeNomad usa o OpenCode por baixo; não tem config própria de API. O mesmo `opencode.json` e o mesmo provider **nvidia-kimi** já valem para sessões abertas pelo CodeNomad.

Para a sessão ter acesso à chave NVIDIA, inicie o CodeNomad a partir de um terminal com o `.env` carregado:

```bash
cd /home/brunoadsba/assistente && set -a && source .env && set +a && codenomad
```

(Use o comando que você usa para abrir o CodeNomad: app desktop, `npx @neuralnomads/codenomad --launch`, etc.)

Dentro do CodeNomad, ao abrir uma sessão OpenCode, use **`/models`** e selecione **Kimi K2.5 (NVIDIA)**. O provider já está conectado; basta escolher o modelo na sessão.

**Alternativa:** coloque `export NVIDIA_API_KEY="sua-chave"` no `~/.bashrc` ou `~/.zshrc` para que qualquer terminal (e o CodeNomad iniciado por ele) já tenha a variável definida.

## Segurança da API Key

- **Nunca** commite a API key no repositório.
- Use sempre a variável de ambiente `NVIDIA_API_KEY` (já referenciada no config).
- Se a chave for exposta, revogue-a no painel da NVIDIA e crie uma nova.

## 3. Parâmetros do script Python (NVIDIA)

O payload que você usou:

- **Endpoint:** `https://integrate.api.nvidia.com/v1/chat/completions`
- **Model:** `moonshotai/kimi-k2.5`
- **Headers:** `Authorization: Bearer <NVIDIA_API_KEY>`, `Accept: text/event-stream` (stream) ou `application/json`
- **Opcional:** `chat_template_kwargs: {"thinking": true}` para modo thinking

No OpenCode, o provider OpenAI-compatible não envia `chat_template_kwargs` por padrão; isso depende de suporte futuro no SDK/OpenCode para parâmetros extras do modelo.
