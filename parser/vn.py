from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz

class VNParser(BaseParser):
    def __init__(self):
        super().__init__("ВН")
        self.url = "https://vn.ru/news/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        articles = soup.select('article.section_news_item')

        for article in articles:
            try:
                title_elem = article.select_one('h2.h2_section')
                link_elem = article.select_one('div.section_news_item_content_title a')
                description_elem = article.select_one('div.section_news_item_content_preview')

                if not title_elem or not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = link_elem["href"]
                description = description_elem.get_text(strip=True) if description_elem else ""

                base_url = "https://vn.ru"
                full_link = link if link.startswith("http") else f"{base_url}{link}"

                # Формируем текущую дату и время
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

                if len(news_list) >= 10:
                    break

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list
