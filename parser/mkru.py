from .baseParser import BaseParser
from models import NewsItem


class MKParser(BaseParser):
    def __init__(self):
        super().__init__("МК Ру")
        self.url = "https://novos.mk.ru/news/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        sections = soup.select('section.news-listing__day-group')

        for section in sections:
            try:
                date_elem = section.select_one('h2.news-listing__day-date')
                date = date_elem.get_text(strip=True)

                news_items = section.select('li.news-listing__item')
                for item in news_items:

                    title_elem = item.select_one('h3.news-listing__item-title')
                    link_elem = item.select_one('a.news-listing__item-link')
                    time_elem = item.select_one('span.news-listing__item-time')

                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem["href"]
                        time = time_elem.get_text(strip=True) if time_elem else ""

                        base_url = "https://novos.mk.ru"
                        full_link = link if link.startswith("http") else f"{base_url}{link}"
                        full_date = f"{date} {time}".strip() if time else date

                        news_item = NewsItem(
                            title=title,
                            link=full_link,
                            date=full_date,
                            source=self.source_name,
                        )
                        news_list.append(news_item)

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list[:10]
