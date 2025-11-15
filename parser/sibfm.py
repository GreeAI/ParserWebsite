from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz


class SibFMParser(BaseParser):
    def __init__(self):
        super().__init__("Сиб ФМ")
        self.url = "https://sib.fm/publications/news"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_items = soup.select('div.news__item')
        news_list = []

        for item in news_items:
            try:
                title_elem = item.select_one('h2')
                date_elem = item.select_one('div.item-news__date')
                link_elem = item.select_one("a.item-news__title")

                base_url = "https://sib.fm"

                if title_elem and date_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem["href"]

                    novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                    now = datetime.now(novosibirsk_tz)
                    date = now.strftime("%d.%m.%Y %H:%M")

                    news_item = NewsItem(
                        title=title,
                        link=link if link.startswith('http') else f"{base_url}{link}",
                        date=date,
                        source=self.source_name
                    )
                    news_list.append(news_item)

                    if len(news_list) >= 10:
                        break

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list