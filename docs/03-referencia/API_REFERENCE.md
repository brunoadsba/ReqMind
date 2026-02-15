# 🔧 API Reference - Assistente Digital

## Índice

1. [Modelos de IA](#modelos-de-ia)
2. [APIs Externas](#apis-externas)
3. [Configuração](#configuração)
4. [Limites e Quotas](#limites-e-quotas)
5. [Códigos de Erro](#códigos-de-erro)

---

## Modelos de IA

### Groq

**Base URL:** `https://api.groq.com/openai/v1`  
**Documentação:** https://console.groq.com/docs

#### Chat (Llama 3.3 70B Versatile)

**Modelo:** `llama-3.3-70b-versatile`

**Especificações:**
- **Contexto:** 128K tokens
- **Velocidade:** ~300 tokens/s
- **Custo:** Gratuito (tier free)
- **Uso:** Conversação geral, raciocínio, tool calling

**Exemplo de Uso:**
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Você é um assistente útil"},
        {"role": "user", "content": "Olá!"}
    ],
    temperature=0.7,
    max_tokens=2048
)

print(response.choices[0].message.content)
```

**Tool Calling:**
```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Obtém clima de uma cidade",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    ],
    tool_choice="auto"
)
```

**Comportamento no bot:**
- Se a API retornar **429 (rate limit)**, o bot tenta (1) **Kimi K2.5** via NVIDIA (se `NVIDIA_API_KEY` estiver definida); (2) se não houver chave ou Kimi falhar, **resposta a partir da memória RAG** (busca por "NR-29" ou "NR" na pergunta; truncamento em fronteira de frase, aviso "(Resumo truncado.)"); (3) sem resultado RAG, devolve mensagem com tempo estimado (ex.: "Tente novamente em cerca de 6 minutos").
- Erros de tool calling (400) disparam nova chamada sem ferramentas antes de falhar.

---

#### Vision (Llama 4 Scout 17B)

**Modelo:** `meta-llama/llama-4-scout-17b-16e-instruct`

**Especificações:**
- **Contexto:** 16K tokens
- **Imagens:** Até 4 por requisição
- **Formatos:** JPG, PNG, WebP, base64
- **Tamanho máximo:** 20MB por imagem
- **Custo:** Gratuito (tier free)

**Exemplo de Uso:**
```python
import base64

# Lê imagem
with open("image.jpg", "rb") as f:
    img_data = base64.b64encode(f.read()).decode('utf-8')

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Descreva esta imagem"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_data}"
                }
            }
        ]
    }],
    temperature=0.5,
    max_completion_tokens=512
)
```

**Múltiplas Imagens:**
```python
content = [{"type": "text", "text": "Compare estas imagens"}]

for img_path in ["img1.jpg", "img2.jpg", "img3.jpg"]:
    with open(img_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
        })

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[{"role": "user", "content": content}]
)
```

---

#### NVIDIA (Kimi K2.5) – Fallback em 429

**Base URL:** `https://integrate.api.nvidia.com/v1/chat/completions`

**Modelo:** `moonshotai/kimi-k2.5`

**Uso no bot:** Quando o Groq retorna 429, o agent chama a API NVIDIA com o mesmo contexto (timeout **20 s** para não bloquear o usuário se a API estiver lenta). Resposta apenas em texto (sem tool calling). Requer `NVIDIA_API_KEY` no `.env`.

**Exemplo (fora do bot):**
```python
import requests, os
url = "https://integrate.api.nvidia.com/v1/chat/completions"
r = requests.post(url, headers={
    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
    "Content-Type": "application/json"
}, json={
    "model": "moonshotai/kimi-k2.5",
    "messages": [{"role": "user", "content": "Olá!"}],
    "max_tokens": 4096, "temperature": 0.7, "stream": False,
    "chat_template_kwargs": {"thinking": True}
}, timeout=20)
print(r.json()["choices"][0]["message"]["content"])
```

---

#### Audio (Whisper Large v3 Turbo)

**Modelo:** `whisper-large-v3-turbo`

**Especificações:**
- **Idiomas:** 99+ idiomas
- **Formatos:** MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
- **Tamanho máximo:** 25MB
- **Duração máxima:** 2 horas
- **Velocidade:** ~10x tempo real
- **Custo:** Gratuito (tier free)

**Exemplo de Uso:**
```python
with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo",
        response_format="text",  # ou "json", "verbose_json"
        language="pt"  # opcional
    )

print(transcription)
```

**Com Timestamps:**
```python
transcription = client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3-turbo",
    response_format="verbose_json",
    timestamp_granularities=["word"]
)

for word in transcription.words:
    print(f"{word.start}s - {word.end}s: {word.word}")
```

---

### ElevenLabs

**Base URL:** `https://api.elevenlabs.io/v1`  
**Documentação:** https://elevenlabs.io/docs

#### Text-to-Speech

**Modelo:** `eleven_multilingual_v2`  
**Voz:** `ErXwobaYiN019PkySvjV` (Antoni - masculina)

**Especificações:**
- **Idiomas:** 29 idiomas incluindo PT-BR
- **Formatos:** MP3, PCM
- **Taxa de amostragem:** 44.1kHz
- **Bitrate:** 128kbps
- **Custo:** 10.000 caracteres/mês (free)

**Exemplo de Uso:**
```python
from elevenlabs import ElevenLabs, VoiceSettings

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

audio = client.text_to_speech.convert(
    text="Olá, como posso ajudar?",
    voice_id="ErXwobaYiN019PkySvjV",
    model_id="eleven_multilingual_v2",
    voice_settings=VoiceSettings(
        stability=0.7,
        similarity_boost=0.85,
        style=0.3,
        use_speaker_boost=True
    ),
    output_format="mp3_44100_128"
)

# Salva áudio
audio_bytes = b"".join(audio)
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

**Vozes Disponíveis:**
```python
voices = client.voices.get_all()

for voice in voices.voices:
    print(f"{voice.name} ({voice.voice_id})")
    print(f"  Idiomas: {voice.labels.get('accent', 'N/A')}")
    print(f"  Gênero: {voice.labels.get('gender', 'N/A')}")
```

---

## APIs Externas

### OpenWeatherMap

**Base URL:** `http://api.openweathermap.org/data/2.5`  
**Documentação:** https://openweathermap.org/api

#### Current Weather

**Endpoint:** `/weather`

**Parâmetros:**
- `q` - Nome da cidade (ex: "São Paulo,BR")
- `appid` - API key
- `units` - Sistema de unidades ("metric", "imperial")
- `lang` - Idioma ("pt_br")

**Exemplo:**
```python
import requests

api_key = os.getenv("OPENWEATHER_API_KEY")
city = "São Paulo"

url = f"http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": city,
    "appid": api_key,
    "units": "metric",
    "lang": "pt_br"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Temperatura: {data['main']['temp']}°C")
print(f"Descrição: {data['weather'][0]['description']}")
```

**Resposta:**
```json
{
  "main": {
    "temp": 25.5,
    "feels_like": 26.2,
    "humidity": 65
  },
  "weather": [{
    "description": "céu limpo"
  }],
  "wind": {
    "speed": 3.5
  }
}
```

**Limites:**
- **Free:** 1.000 chamadas/dia
- **Rate limit:** 60 chamadas/minuto

---

### NewsAPI

**Base URL:** `https://newsapi.org/v2`  
**Documentação:** https://newsapi.org/docs

#### Everything

**Endpoint:** `/everything`

**Parâmetros:**
- `q` - Termo de busca
- `language` - Idioma ("pt")
- `pageSize` - Número de resultados (1-100)
- `apiKey` - API key

**Exemplo:**
```python
api_key = os.getenv("NEWS_API_KEY")
topic = "tecnologia"

url = "https://newsapi.org/v2/everything"
params = {
    "q": topic,
    "language": "pt",
    "pageSize": 5,
    "apiKey": api_key
}

response = requests.get(url, params=params)
data = response.json()

for article in data['articles']:
    print(f"Título: {article['title']}")
    print(f"Fonte: {article['source']['name']}")
    print(f"URL: {article['url']}")
```

**Limites:**
- **Free:** 100 requisições/dia
- **Developer:** 1.000 requisições/dia

---

## Configuração

### Variáveis de Ambiente (.env)

```bash
# Telegram (OBRIGATÓRIO)
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Groq (OBRIGATÓRIO)
GROQ_API_KEY=gsk_abcdefghijklmnopqrstuvwxyz1234567890

# NVIDIA – Kimi K2.5 (OPCIONAL – fallback quando Groq retorna 429)
NVIDIA_API_KEY=nvapi-...

# ElevenLabs (OPCIONAL - TTS)
ELEVENLABS_API_KEY=sk_abcdefghijklmnopqrstuvwxyz1234567890

# Email para Lembretes (OPCIONAL)
EMAIL_ADDRESS=seu_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=sua_senha_app_gmail

# OpenWeatherMap (OPCIONAL)
OPENWEATHER_API_KEY=abcdefghijklmnopqrstuvwxyz123456

# NewsAPI (OPCIONAL)
NEWS_API_KEY=abcdefghijklmnopqrstuvwxyz123456

# Legado (não mais usado)
GLM_API_KEY=...
KIMI_API_KEY=...
OPENROUTER_API_KEY=...
```

### Obter API Keys

#### Groq
1. Acesse: https://console.groq.com
2. Crie uma conta
3. Vá em "API Keys"
4. Clique em "Create API Key"
5. Copie a chave

#### NVIDIA (Kimi K2.5 – fallback)
1. Acesse: https://build.nvidia.com/ ou console da NVIDIA
2. Crie/obtenha uma API key para NIM (NVIDIA AI)
3. No `.env`: `NVIDIA_API_KEY=nvapi-...`

#### ElevenLabs
1. Acesse: https://elevenlabs.io
2. Crie uma conta
3. Vá em "Profile" → "API Keys"
4. Copie a chave

#### OpenWeatherMap
1. Acesse: https://openweathermap.org/api
2. Crie uma conta
3. Vá em "API keys"
4. Gere uma nova chave

#### NewsAPI
1. Acesse: https://newsapi.org
2. Crie uma conta
3. Copie a API key do dashboard

#### Gmail (para lembretes)
1. Acesse: https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Vá em "Senhas de app"
4. Gere senha para "Email"
5. Use essa senha no `.env`

---

## Limites e Quotas

### Groq (Free Tier)

| Modelo | RPM | RPD | TPM | TPD |
|--------|-----|-----|-----|-----|
| Llama 3.3 70B | 30 | 14.400 | 6.000 | 2.880.000 |
| Llama 4 Scout | 30 | 14.400 | 6.000 | 2.880.000 |
| Whisper Turbo | 20 | 9.600 | - | - |

**Legenda:**
- RPM: Requisições por minuto
- RPD: Requisições por dia
- TPM: Tokens por minuto
- TPD: Tokens por dia

### ElevenLabs (Free Tier)

- **Caracteres/mês:** 10.000
- **Vozes:** Todas disponíveis
- **Qualidade:** Alta

### OpenWeatherMap (Free Tier)

- **Chamadas/dia:** 1.000
- **Chamadas/minuto:** 60
- **Dados:** Clima atual

### NewsAPI (Free Tier)

- **Requisições/dia:** 100
- **Resultados/requisição:** 100
- **Histórico:** 1 mês

### Telegram Bot API

- **Mensagens/segundo:** 30
- **Mensagens/minuto:** 20 por chat
- **Tamanho de arquivo:** 50MB (download), 20MB (upload)
- **Timeout:** 60 segundos

---

## Códigos de Erro

### Groq

| Código | Descrição | Solução |
|--------|-----------|---------|
| 400 | Bad Request | Verifique parâmetros |
| 401 | Unauthorized | API key inválida |
| 429 | Rate Limit | Aguarde e tente novamente |
| 500 | Server Error | Tente novamente mais tarde |

### ElevenLabs

| Código | Descrição | Solução |
|--------|-----------|---------|
| 401 | Invalid API Key | Verifique API key |
| 402 | Quota Exceeded | Upgrade ou aguarde reset |
| 422 | Validation Error | Verifique parâmetros |

### Telegram

| Código | Descrição | Solução |
|--------|-----------|---------|
| 400 | Bad Request | Parâmetros inválidos |
| 401 | Unauthorized | Token inválido |
| 403 | Forbidden | Bot bloqueado pelo usuário |
| 429 | Too Many Requests | Rate limit excedido |

---

## Exemplos Completos

### Chat com Tool Calling

```python
from groq import Groq
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define ferramenta
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Obtém clima de uma cidade",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nome da cidade"
                }
            },
            "required": ["city"]
        }
    }
}]

# Mensagem do usuário
messages = [
    {"role": "user", "content": "Qual o clima em São Paulo?"}
]

# Primeira chamada
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Verifica se há tool call
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    
    # Executa ferramenta
    args = json.loads(tool_call.function.arguments)
    result = get_weather(args['city'])
    
    # Adiciona resultado
    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": [tool_call]
    })
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    })
    
    # Segunda chamada com resultado
    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    print(final_response.choices[0].message.content)
```

---

### Análise de Vídeo Completa

```python
import subprocess
import base64
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Extrai frames do vídeo
subprocess.run([
    "ffmpeg", "-i", "video.mp4",
    "-vf", "fps=0.2",  # 1 frame a cada 5s
    "-q:v", "5",
    "frame_%03d.jpg"
])

# 2. Seleciona 3 frames
frames = ["frame_001.jpg", "frame_005.jpg", "frame_010.jpg"]

# 3. Prepara conteúdo
content = [{"type": "text", "text": "Analise este vídeo"}]

for frame in frames:
    with open(frame, "rb") as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
        })

# 4. Analisa com Vision
response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[{"role": "user", "content": content}],
    max_completion_tokens=1024
)

print(response.choices[0].message.content)

# 5. Transcreve áudio
subprocess.run([
    "ffmpeg", "-i", "video.mp4",
    "-vn", "-acodec", "mp3",
    "audio.mp3"
])

with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo"
    )

print(f"\nTranscrição: {transcription}")
```

---

## APIs Internas (Novas - v1.1)

### SecureFileManager API

**Localização:** `security/file_manager.py`

#### secure_files.temp_file()

Cria um arquivo temporário seguro com auto-cleanup.

```python
from security import secure_files

async with secure_files.temp_file(suffix='.mp4') as path:
    # path é um Path object
    await download_video(path)
    await process_video(path)
    # Arquivo automaticamente deletado
```

**Parâmetros:**
- `suffix` (str): Extensão do arquivo (ex: '.mp4', '.jpg')
- `prefix` (str, opcional): Prefixo do nome (padrão: 'moltbot_')

**Retorna:**
- `Path`: Caminho do arquivo temporário

**Extensões Permitidas:**
- Vídeo: mp4, mov, avi, mkv
- Áudio: mp3, ogg, wav, m4a
- Imagem: jpg, jpeg, png, gif, webp
- Documento: xlsx, xls, csv, docx, md, txt

**Erros:**
- `ValueError`: Se extensão não for permitida

---

#### secure_files.sanitize_filename()

Remove caracteres perigosos de nomes de arquivo.

```python
from security import secure_files

safe_name = secure_files.sanitize_filename("../../../etc/passwd.txt")
# Retorna: "passwd.txt"

safe_name = secure_files.sanitize_filename("arquivo<script>.txt")
# Retorna: "arquivo_script_.txt"
```

**Parâmetros:**
- `filename` (str): Nome do arquivo original

**Retorna:**
- `str`: Nome sanitizado

**Erros:**
- `ValueError`: Se extensão não for permitida

---

#### secure_files.validate_mime_type()

Valida MIME type real do arquivo.

```python
from security import secure_files

is_valid = secure_files.validate_mime_type(
    file_path,
    ['image/jpeg', 'image/png']
)
# Retorna: True ou False
```

**Parâmetros:**
- `file_path` (Path): Caminho do arquivo
- `expected_types` (List[str]): Lista de MIME types esperados

**Retorna:**
- `bool`: True se válido, False caso contrário

---

### SafeSubprocessExecutor API

**Localização:** `security/executor.py`

#### SafeSubprocessExecutor.run()

Executa comando de forma assíncrona e segura.

```python
from security import SafeSubprocessExecutor

success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video_path),
    "-vframes", "1", str(frame_path)
])

if success:
    print(f"Sucesso: {stdout}")
else:
    print(f"Erro: {stderr}")
```

**Parâmetros:**
- `cmd` (List[str]): Lista de argumentos do comando
- `timeout` (int, opcional): Timeout em segundos (padrão: 30)
- `cwd` (str, opcional): Diretório de trabalho
- `env` (dict, opcional): Variáveis de ambiente

**Retorna:**
- `Tuple[bool, str, str]`: (sucesso, stdout, stderr)

**Comandos Permitidos:**
- `ffmpeg`
- `ffprobe`
- `tesseract`
- `python`, `python3`

**Erros:**
- Retorna `(False, "", "Comando não permitido")` se comando não estiver na whitelist
- Retorna `(False, "", "Argumento suspeito...")` se detectar injection
- Retorna `(False, "", "Timeout...")` se exceder timeout

---

### Retry Decorator API

**Localização:** `utils/retry.py`

#### retry_with_backoff()

Decorator para retry com exponential backoff.

```python
from utils import retry_with_backoff

@retry_with_backoff(
    max_retries=3,
    initial_delay=1.0,
    max_delay=10.0,
    exceptions=(ConnectionError, TimeoutError)
)
async def call_external_api():
    response = await http_client.get("https://api.example.com")
    return response.json()
```

**Parâmetros:**
- `max_retries` (int): Número máximo de tentativas (padrão: 3)
- `initial_delay` (float): Delay inicial em segundos (padrão: 1.0)
- `max_delay` (float): Delay máximo em segundos (padrão: 10.0)
- `exceptions` (tuple): Exceções para capturar (padrão: (Exception,))

**Comportamento:**
- Tentativa 1: Delay de ~1.0s + jitter
- Tentativa 2: Delay de ~2.0s + jitter
- Tentativa 3: Delay de ~4.0s + jitter (capped em max_delay)
- Após max_retries: Propaga a exceção

---

### Config API

**Localização:** `config/settings.py`

#### config (instância global)

Acesso centralizado a todas as configurações.

```python
from config import config

# Paths
base_dir = config.BASE_DIR       # MOLTBOT_DIR ou default
 temp_dir = config.TEMP_DIR      # MOLTBOT_TEMP ou /tmp/moltbot_secure
data_dir = config.DATA_DIR       # BASE_DIR / 'dados'

# Modelos
vision_model = config.GROQ_MODEL_VISION
chat_model = config.GROQ_MODEL_CHAT
whisper_model = config.WHISPER_MODEL

# Limites
max_size = config.MAX_FILE_SIZE_MB      # 50
max_duration = config.MAX_VIDEO_DURATION_MIN  # 10
timeout = config.REQUEST_TIMEOUT        # 30.0

# Segurança
allowed_users = config.ALLOWED_USERS    # List[int]
```

**Variáveis de Ambiente:**
```bash
# Paths
MOLTBOT_DIR=/home/brunoadsba/clawd/moltbot-setup
MOLTBOT_TEMP=/tmp/moltbot_secure

# Segurança
ALLOWED_USERS=123456789,987654321

# Outras
LOG_LEVEL=INFO
```

**Propriedades Disponíveis:**
- `BASE_DIR` (Path): Diretório base do projeto
- `TEMP_DIR` (Path): Diretório de arquivos temporários
- `DATA_DIR` (Path): Diretório de dados
- `GROQ_MODEL_VISION` (str): Modelo de visão
- `GROQ_MODEL_CHAT` (str): Modelo de chat
- `WHISPER_MODEL` (str): Modelo de transcrição
- `MAX_FILE_SIZE_MB` (int): Tamanho máximo de arquivo
- `MAX_VIDEO_DURATION_MIN` (int): Duração máxima de vídeo
- `REQUEST_TIMEOUT` (float): Timeout de requisições
- `ALLOWED_USERS` (List[int]): IDs de usuários autorizados

---

## Referências

- **Groq:** https://console.groq.com/docs
- **ElevenLabs:** https://elevenlabs.io/docs
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **OpenWeatherMap:** https://openweathermap.org/api
- **NewsAPI:** https://newsapi.org/docs
- **FFmpeg:** https://ffmpeg.org/documentation.html
- **yt-dlp:** https://github.com/yt-dlp/yt-dlp

---

## Suporte

Para problemas com APIs:
- **Groq:** https://console.groq.com/support
- **ElevenLabs:** support@elevenlabs.io
- **Telegram:** https://core.telegram.org/bots/support

Para problemas com o Assistente Digital:
- Consulte `TROUBLESHOOTING.md`
- Veja logs: `tail -f bot.log`
