from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz


class OMParser(BaseParser):
    def __init__(self):
        super().__init__("ОМ")
        self.url = "https://www.nsk.om1.ru/news/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        blocks = soup.select('div.col.s12.t-left-column')

        for block in blocks:
            try:
                title_elem = block.select_one('a.new-news-piece__link')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem["href"]

                base_url = "https://www.nsk.om1.ru"
                full_link = link if link.startswith("http") else f"{base_url}{link}"

                novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                now = datetime.now(novosibirsk_tz)
                date = now.strftime("%d.%m.%Y %H:%M")

                # Создаем объект новости
                news_item = NewsItem(
                    title=title,
                    link=full_link,
                    date=date,
                    source=self.source_name,
                )
                news_list.append(news_item)

                if len(news_list) >= 10:
                    break

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list