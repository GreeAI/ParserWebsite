from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
from logs.logger import logging
import pytz

class NSKTVParser(BaseParser):
    def __init__(self):
        super().__init__("НСК ТВ")
        self.url = "https://www.nsktv.ru/news/"

    def parse(self):
        logging.info("Запуск парсера НСК ТВ")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        base_url = "https://www.nsktv.ru"

        # пробуем новую верстку
        blocks = soup.select('a.news_block')
        if not blocks:
            # fallback на старую верстку (если вдруг изменят)
            blocks = soup.select('div.news_block')

        for block in blocks:
            try:
                # --- новый вариант ---
                title_elem = block.select_one('p.news_info-title')
                description_elem = block.select_one('p.news_info-description')

                # --- fallback ---
                if not title_elem:
                    title_elem = block.select_one('h3.news_title')
                if not description_elem:
                    description_elem = block.select_one('div.news_description')

                link = block.get("href")

                if title_elem and link:
                    title = title_elem.get_text(strip=True)
                    full_link = link if link.startswith("http") else f"{base_url}{link}"
                    description = description_elem.get_text(strip=True) if description_elem else ""

                    novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                    now = datetime.now(novosibirsk_tz)
                    date = now.strftime("%d.%m.%Y %H:%M")

                    news_item = NewsItem(
                        title=title,
                        link=full_link,
                        date=date,
                        source=self.source_name,
                        content=description
                    )
                    news_list.append(news_item)

                    if len(news_list) >= 20:  # можно увеличить лимит
                        break

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list
