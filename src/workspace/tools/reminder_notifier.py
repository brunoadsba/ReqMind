"""Sistema de notificação de lembretes por email e Telegram"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
import asyncio
import logging
from telegram import Bot

from config.settings import config

logger = logging.getLogger(__name__)


class ReminderNotifier:
    def __init__(self):
        self.email = os.getenv("EMAIL_ADDRESS")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.password = os.getenv("SMTP_PASSWORD")
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telegram_chat_id = int(os.getenv("TELEGRAM_CHAT_ID", "6974901522"))
        # Storage persistente em config.DATA_DIR (config.REMINDERS_FILE)
        self.reminders_file = str(config.REMINDERS_FILE)
        self.tz = pytz.timezone("America/Sao_Paulo")
        self.bot = None

    def send_email(self, subject: str, body: str):
        """Envia email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email enviado: {subject}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False

    async def send_telegram(self, message: str):
        """Envia mensagem no Telegram"""
        try:
            if not self.bot:
                self.bot = Bot(token=self.telegram_token)

            await self.bot.send_message(chat_id=self.telegram_chat_id, text=message)
            logger.info("Mensagem Telegram enviada")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar Telegram: {e}")
            return False

    async def check_reminders(self):
        """Verifica lembretes pendentes"""
        try:
            if not os.path.exists(self.reminders_file):
                return

            with open(self.reminders_file, "r") as f:
                reminders = json.load(f)

            now = datetime.now(self.tz)
            pending_reminders = []
            sent_reminders = []

            for reminder in reminders:
                reminder_time = datetime.fromisoformat(reminder["timestamp"])

                # Se o lembrete é para agora (com margem de 1 minuto)
                diff = (reminder_time - now).total_seconds()

                if -60 <= diff <= 60:  # Dentro de 1 minuto
                    # Envia email
                    subject = f"🔔 Lembrete: {reminder['text']}"
                    body = f"""Olá!

Este é seu lembrete agendado:

📝 {reminder["text"]}
🕐 Horário: {reminder["datetime"]}

---
Enviado por Moltbot
"""

                    # Envia Telegram
                    telegram_msg = (
                        f"🔔 **LEMBRETE**\n\n📝 {reminder['text']}\n🕐 {reminder['datetime']}"
                    )

                    email_sent = self.send_email(subject, body)
                    telegram_sent = await self.send_telegram(telegram_msg)

                    if email_sent or telegram_sent:
                        sent_reminders.append(reminder)
                        logger.info(f"Lembrete enviado: {reminder['text']}")
                elif diff > 60:
                    # Lembrete futuro
                    pending_reminders.append(reminder)

            # Atualiza arquivo removendo lembretes enviados
            if sent_reminders:
                with open(self.reminders_file, "w") as f:
                    json.dump(pending_reminders, f, indent=2)

        except Exception as e:
            logger.error(f"Erro ao verificar lembretes: {e}")

    def list_pending_reminders(self) -> list:
        """Retorna lista de lembretes pendentes ordenados por data/hora."""
        try:
            if not os.path.exists(self.reminders_file):
                return []

            with open(self.reminders_file, "r") as f:
                reminders = json.load(f)

            now = datetime.now(self.tz)
            pending = []

            for r in reminders:
                try:
                    reminder_time = datetime.fromisoformat(r["timestamp"])
                    if reminder_time > now:
                        pending.append(
                            {
                                "text": r.get("text", ""),
                                "datetime": r.get("datetime", ""),
                                "timestamp": r["timestamp"],
                            }
                        )
                except (KeyError, ValueError):
                    continue

            pending.sort(key=lambda x: x["timestamp"])
            return pending
        except Exception as e:
            logger.error(f"Erro ao listar lembretes: {e}")
            return []

    async def start_monitoring(self):
        """Inicia monitoramento de lembretes"""
        logger.info("Sistema de lembretes iniciado (Email + Telegram)")
        while True:
            await self.check_reminders()
            await asyncio.sleep(60)  # Verifica a cada 1 minuto


# Instância global
notifier = ReminderNotifier()
