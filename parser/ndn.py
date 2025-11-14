from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz


class NDNParser(BaseParser):
    def __init__(self):
        super().__init__("НДН")
        self.url = "https://ndn.info/novosti/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        articles = soup.select('article.jeg_post')

        for article in articles:
            try:
                title_elem = article.select_one('h3.jeg_post_title a')
                if not title_elem:
                    continue

                content_elem = article.select_one('div.jeg_post_excerpt')
                if not content_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem["href"]
                content = content_elem.get_text(strip=True)

                full_link = link

                novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                now = datetime.now(novosibirsk_tz)
                date = now.strftime("%d.%m.%Y %H:%M")

                # Создаем объект новости
                news_item = NewsItem(
                    title=title,
                    link=full_link,
                    date=date,
                    source=self.source_name,
                    content=content,
                )
                news_list.append(news_item)

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list