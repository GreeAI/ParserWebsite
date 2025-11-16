from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
from logs.logger import logging
import pytz



class NSKAIFParser(BaseParser):
    def __init__(self):
        super().__init__("Документы и Факты")
        self.url = "https://nsk.aif.ru/news"

    def parse(self):
        logging.info("Запуск парсера Документы и Факты nskaif")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        # Ищем все новостные блоки
        items = soup.select('div.list_item')

        for item in items:
            try:
                text_box = item.select_one('div.text_box.no_title_element_js')
                if not text_box:
                    continue

                title_elem = text_box.select_one('a span.item_text__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link_elem = title_elem.find_parent('a')
                link = link_elem['href'] if link_elem else ""

                content_elem = text_box.select_one('span:last-child')
                content = ""
                if content_elem and content_elem.get_text(strip=True):
                    content = content_elem.get_text(strip=True)

                novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                now = datetime.now(novosibirsk_tz)
                date = now.strftime("%d.%m.%Y %H:%M")

                full_link = link if link.startswith("http") else f"https://nsk.aif.ru{link}"

                news_item = NewsItem(
                    title=title,
                    link=full_link,
                    date=date,
                    source=self.source_name,
                    content=content,
                )
                news_list.append(news_item)

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list