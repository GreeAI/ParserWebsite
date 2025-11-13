from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz


class NSKTVParser(BaseParser):
    def __init__(self):
        super().__init__("НСК ТВ")
        self.url = "https://www.nsktv.ru/news/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        base_url = "https://www.nsktv.ru"

        blocks = soup.select('a.news_block')

        for block in blocks:
            try:
                title_elem = block.select_one('p.news_info-title')
                description_elem = block.select_one('p.news_info-description')
                link = block.get("href")

                if title_elem and description_elem and link:
                    title = title_elem.get_text(strip=True)
                    full_link = link if link.startswith("http") else f"{base_url}{link}"
                    description = description_elem.get_text(strip=True)

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

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list
