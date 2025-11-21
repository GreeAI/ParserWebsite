import asyncio
import re
import pytz
from datetime import datetime

from telethon.sync import TelegramClient
from models import NewsItem
from logs.logger import logging
from config import TG_ID, TG_HASH

api_id = int(TG_ID)
api_hash = TG_HASH

channels = [
    "mvd_54",
    "gibddnso",
    "zstproc",
    "vm_sut",
    "utsibfo",
    "nsk54_official",
    "spasatelimass",
    "mchs54",
    "prokuratura_nso",
    "nsksledcom",
    "CODD_NSO",
    "nskkp",
    "testfornsk",
]

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


class TelegramParser:
    def __init__(self, limit=5, session_name="tg_parser_session"):
        self.source_name = "telegram channels"
        self.limit = limit
        self.session_name = session_name

    def _ensure_event_loop(self):
        # Если мы в потоке APScheduler, у него нет loop — создаём и назначаем
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logging.debug("Asyncio event loop создан и назначен для текущего потока")

    def _parse_channel(self, client, channel):
        news_list = []
        try:
            for message in client.iter_messages(channel, limit=self.limit):
                if not message:
                    continue

                # Берём текст из message.text или message.message
                text = getattr(message, "text", None) or getattr(message, "message", None)
                if not text or not text.strip():
                    continue

                title = re.split(r"[.!?\n]", text.strip(), maxsplit=1)[0].strip()
                date = message.date.astimezone(novosibirsk_tz).strftime("%d.%m.%Y %H:%M")
                link = f"https://t.me/{channel}/{message.id}"

                news_list.append(
                    NewsItem(
                        title=title,
                        link=link,
                        date=date,
                        source=f"TG {channel}",
                    )
                )
        except Exception as e:
            logging.warning(f"❌ TG {channel}: ошибка получения сообщений: {e}")
        return news_list

    def parse(self):
        """Синхронный интерфейс для scheduler — с корректным event loop в потоке"""
        self._ensure_event_loop()

        collected = []
        try:
            # Явно создаём клиента с текущим loop (назначенным выше)
            loop = asyncio.get_event_loop()
            client = TelegramClient(self.session_name, api_id, api_hash, loop=loop)
            client.connect()

            if not client.is_user_authorized():
                logging.warning("Сессия Telethon не авторизована. Проверь .session файл.")
                # Здесь можно прервать или попытаться client.start(), если есть интерактивный ввод
                client.disconnect()
                return []

            for channel in channels:
                news = self._parse_channel(client, channel)
                logging.info(f"✅ TG {channel}: {len(news)} найдено")
                collected.extend(news)

            client.disconnect()

        except Exception as e:
            logging.warning(f"Ошибка Telegram парсера: {e}")
            return []

        return collected
