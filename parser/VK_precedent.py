import time
import re
import pytz

from models import NewsItem
from .vkBaseParser import VkBaseParser
from datetime import datetime
from logs.logger import logging




class VKPrecedentParser(VkBaseParser):
    def __init__(self):
        super().__init__(source_name="precedent1995")
        self.url = "https://api.vk.com/method/wall.get"  # URL VK API

    def parse(self):
        """Парсинг через VK API"""
        logging.info("Запуск парсера ВК precedent1995")
        time.sleep(1)
        data = self.get_page(self.url)
        news_list = []

        for post in data:
            try:
                ts = post.get("date")
                if ts:
                    novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                    date = datetime.fromtimestamp(ts, tz=novosibirsk_tz).strftime("%d.%m.%Y %H:%M")
                else:
                    date = datetime.now(pytz.timezone("Asia/Novosibirsk")).strftime("%d.%m.%Y %H:%M")

                text = post.get("text", "").strip()
                if text:
                    title = re.split(r'[.!?\n]', text, maxsplit=1)[0].strip()
                else:
                    title = "Без заголовка"

                link = f"https://vk.com/{self.source_name}?w=wall{post['owner_id']}_{post['id']}"

                news_item = NewsItem(
                    title=title,
                    link=link,
                    date=date,
                    source="ВК Прецедент",
                )
                news_list.append(news_item)

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue
        # Обработка данных из API
        # data будет содержать посты со стены группы
        return news_list