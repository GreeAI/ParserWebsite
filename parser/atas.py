from .baseParser import BaseParser
from models import NewsItem
from datetime import datetime
import pytz


class ATASParser(BaseParser):
    def __init__(self):
        super().__init__("АТАС Инфо")
        self.url = "https://atas.info/news"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []
        items = soup.select('div.mb-8')

        for item in items:
            try:
                link_elem = item.select_one('a[href]')
                if not link_elem:
                    continue

                link = link_elem["href"]

                title_elem = link_elem.select_one('div.DesktopListItem_title__zM5AO')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                content_elem = link_elem.select_one('div.DesktopListItem_lead__fqYld')
                content = ""
                if content_elem is not None:
                    content = content_elem.get_text(strip=True)

                novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
                now = datetime.now(novosibirsk_tz)
                date = now.strftime("%d.%m.%Y %H:%M")


                # Создаем объект новости
                news_item = NewsItem(
                    title=title,
                    link=link,
                    date=date,
                    source=self.source_name,
                    content=content,
                )
                news_list.append(news_item)

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list