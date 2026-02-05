"""Ferramentas Extras - OCR, Clima, Notícias, etc"""

import os
import requests
import pytesseract
from PIL import Image
import io
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # Backend sem GUI
from datetime import datetime, timedelta
import json
from pathlib import Path


def get_data_dir() -> Path:
    """Retorna o diretório de dados persistente"""
    data_dir = Path.home() / ".assistente" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# 1. OCR - Extrair texto de imagens
async def ocr_extract(image_path: str) -> dict:
    """Extrai texto de imagem usando Tesseract"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="por+eng")
        return {"success": True, "text": text.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# 2. Clima - OpenWeatherMap
async def get_weather(city: str) -> dict:
    """Obtém clima atual de uma cidade"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"success": False, "error": "API key não configurada"}

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt_br"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            weather = {
                "cidade": data["name"],
                "temperatura": f"{data['main']['temp']}°C",
                "sensacao": f"{data['main']['feels_like']}°C",
                "descricao": data["weather"][0]["description"],
                "umidade": f"{data['main']['humidity']}%",
                "vento": f"{data['wind']['speed']} m/s",
            }
            return {"success": True, "weather": weather}
        else:
            return {"success": False, "error": "Cidade não encontrada"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# 3. Notícias - NewsAPI
async def get_news(topic: str = "brasil", limit: int = 5) -> dict:
    """Obtém últimas notícias sobre um tópico"""
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return {"success": False, "error": "API key não configurada"}

        url = f"https://newsapi.org/v2/everything?q={topic}&language=pt&pageSize={limit}&apiKey={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            articles = []
            for article in data.get("articles", [])[:limit]:
                articles.append(
                    {
                        "titulo": article["title"],
                        "fonte": article["source"]["name"],
                        "url": article["url"],
                        "data": article["publishedAt"][:10],
                    }
                )
            return {"success": True, "articles": articles}
        else:
            return {"success": False, "error": "Erro ao buscar notícias"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# 5. Lembretes - Arquivo JSON (sem SQLite)
async def create_reminder(text: str, datetime_str: str) -> dict:
    """Cria um lembrete"""
    try:
        from datetime import datetime
        import pytz
        import json
        import os

        # Timezone de Brasília
        tz_brasilia = pytz.timezone("America/Sao_Paulo")

        # Parse da data/hora
        dt = None
        for fmt in [
            "%d/%m/%Y %H:%M",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y às %Hh",
            "%d/%m/%Y %Hh",
        ]:
            try:
                dt = datetime.strptime(datetime_str, fmt)
                break
            except:
                continue

        if not dt:
            dt = datetime.now(tz_brasilia)

        # Adiciona timezone
        dt = tz_brasilia.localize(dt) if dt.tzinfo is None else dt

        reminder_data = {
            "text": text,
            "datetime": dt.strftime("%d/%m/%Y às %H:%M"),
            "timestamp": dt.isoformat(),
            "created_at": datetime.now(tz_brasilia).strftime("%d/%m/%Y às %H:%M"),
        }

        # Salva em arquivo JSON persistente
        reminders_file = get_data_dir() / "reminders.json"
        reminders = []

        if reminders_file.exists():
            with open(reminders_file, "r") as f:
                reminders = json.load(f)

        reminders.append(reminder_data)

        with open(reminders_file, "w") as f:
            json.dump(reminders, f, indent=2)

        # NÃO salva no SQLite - retorna direto
        return {
            "success": True,
            "message": f"✅ Lembrete criado para {reminder_data['datetime']}",
            "reminder": reminder_data,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# 7. Mapas - Calcular distância
async def calculate_distance(city1: str, city2: str) -> dict:
    """Calcula distância entre duas cidades"""
    try:
        # Usa Nominatim (OpenStreetMap) para geocoding
        def get_coords(city):
            url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
            headers = {"User-Agent": "MoltBot/1.0"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return float(data["lat"]), float(data["lon"])
            return None, None

        lat1, lon1 = get_coords(city1)
        lat2, lon2 = get_coords(city2)

        if not lat1 or not lat2:
            return {"success": False, "error": "Cidade não encontrada"}

        # Fórmula de Haversine
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Raio da Terra em km

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return {
            "success": True,
            "distance_km": round(distance, 2),
            "city1": city1,
            "city2": city2,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# 8. Gráficos Profissionais
async def create_chart(data: dict, chart_type: str = "bar") -> dict:
    """Cria gráfico profissional a partir de dados"""
    try:
        import tempfile
        import numpy as np

        labels = data.get("labels", [])
        values = data.get("values", [])
        title = data.get("title", "Análise de Dados")

        if not labels or not values:
            return {"success": False, "error": "Dados inválidos"}

        # Configuração profissional
        plt.style.use("seaborn-v0_8-darkgrid")
        fig, ax = plt.subplots(figsize=(14, 8))

        # Cores profissionais
        colors = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E", "#BC4B51"]

        if chart_type == "bar":
            bars = ax.bar(
                labels,
                values,
                color=colors[: len(labels)],
                edgecolor="black",
                linewidth=1.2,
            )
            ax.set_ylabel("Valores", fontsize=12, fontweight="bold")

            # Adiciona valores em cima das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:,.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )

            # Grid
            ax.yaxis.grid(True, linestyle="--", alpha=0.7)
            ax.set_axisbelow(True)

        elif chart_type == "line":
            ax.plot(
                labels,
                values,
                marker="o",
                linewidth=3,
                markersize=10,
                color="#2E86AB",
                markerfacecolor="#F18F01",
                markeredgewidth=2,
                markeredgecolor="#2E86AB",
            )
            ax.fill_between(range(len(values)), values, alpha=0.3, color="#2E86AB")
            ax.set_ylabel("Valores", fontsize=12, fontweight="bold")

            # Adiciona valores nos pontos
            for i, (label, value) in enumerate(zip(labels, values)):
                ax.text(
                    i,
                    value,
                    f"{value:,.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                )

            # Grid
            ax.grid(True, linestyle="--", alpha=0.7)

            # Linha de tendência
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            ax.plot(
                labels,
                p(range(len(values))),
                "--",
                color="red",
                linewidth=2,
                alpha=0.7,
                label="Tendência",
            )
            ax.legend(loc="best", fontsize=10)

        elif chart_type == "pie":
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                colors=colors[: len(labels)],
                startangle=90,
                textprops={"fontsize": 11, "fontweight": "bold"},
                explode=[0.05] * len(values),
            )

            # Melhora legibilidade
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(12)
                autotext.set_fontweight("bold")

        # Título profissional
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

        # Rotaciona labels se necessário
        if chart_type != "pie" and len(labels) > 6:
            plt.xticks(rotation=45, ha="right")

        # Estatísticas no rodapé
        if chart_type != "pie":
            stats_text = f"Média: {np.mean(values):,.1f} | Máx: {max(values):,.0f} | Mín: {min(values):,.0f}"
            fig.text(
                0.5,
                0.02,
                stats_text,
                ha="center",
                fontsize=10,
                style="italic",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
            )

        plt.tight_layout()

        # Salva em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()

        return {"success": True, "image_path": temp_file.name}
    except Exception as e:
        return {"success": False, "error": str(e)}


# 11. Geração de Imagens AI
async def generate_image(prompt: str) -> dict:
    """Gera imagem usando Stable Diffusion via Replicate"""
    try:
        api_key = os.getenv("REPLICATE_API_KEY")
        if not api_key:
            return {"success": False, "error": "API key não configurada"}

        import replicate

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"prompt": prompt},
        )

        # Output é uma lista de URLs
        if output and len(output) > 0:
            return {"success": True, "image_url": output[0]}
        else:
            return {"success": False, "error": "Nenhuma imagem gerada"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Schemas para o Agent
OCR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "ocr_extract",
        "description": "Extrai texto de uma imagem (OCR)",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Caminho da imagem"}
            },
            "required": ["image_path"],
        },
    },
}

WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Obtém clima atual de uma cidade",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "Nome da cidade"}},
            "required": ["city"],
        },
    },
}

NEWS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_news",
        "description": "Busca últimas notícias sobre um tópico",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Tópico das notícias"},
                "limit": {
                    "type": "integer",
                    "description": "Número de notícias (padrão: 5)",
                },
            },
            "required": ["topic"],
        },
    },
}

REMINDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_reminder",
        "description": "Cria um lembrete para uma data/hora específica. Use formato brasileiro: DD/MM/YYYY HH:MM",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto do lembrete"},
                "datetime_str": {
                    "type": "string",
                    "description": "Data/hora no formato DD/MM/YYYY HH:MM (ex: 31/01/2026 17:00)",
                },
            },
            "required": ["text", "datetime_str"],
        },
    },
}

DISTANCE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate_distance",
        "description": "Calcula distância entre duas cidades",
        "parameters": {
            "type": "object",
            "properties": {
                "city1": {"type": "string", "description": "Primeira cidade"},
                "city2": {"type": "string", "description": "Segunda cidade"},
            },
            "required": ["city1", "city2"],
        },
    },
}

CHART_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_chart",
        "description": "Cria um gráfico a partir de dados",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Dados do gráfico com 'labels', 'values' e 'title'",
                },
                "chart_type": {
                    "type": "string",
                    "description": "Tipo: 'bar', 'line' ou 'pie'",
                    "enum": ["bar", "line", "pie"],
                },
            },
            "required": ["data"],
        },
    },
}

IMAGE_GEN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Gera uma imagem usando IA a partir de uma descrição em texto",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Descrição da imagem a ser gerada",
                }
            },
            "required": ["prompt"],
        },
    },
}
