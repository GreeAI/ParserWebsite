from .baseParser import BaseParser
from models import NewsItem


class NSKParser(BaseParser):
    def __init__(self):
        super().__init__("НСК Новости")
        self.url = "https://nsknews.info/news"


    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_items = soup.select('div.nn-news-article-hor')
        news_list = []

        for item in news_items:
            try:
                img = item.select_one('img')
                title = img.get('alt', '').strip() if img else ""


                title_elem = item.select_one('a')
                link = title_elem.get('href', '') if title_elem else ""

                date_elem = item.select_one('.nn-news-article-hor__date')
                date = date_elem.text.strip() if date_elem else "Сегодня"

                if not title or not link:
                    continue

                base_url = "https://nsknews.info"  # Новости без /news
                if not link.startswith('http'):
                    link = base_url + link if link.startswith('/') else f"{self.url}/{link}"

                news_item = NewsItem(
                    title=title,
                    link=link,
                    date=date,
                    source=self.source_name
                )

                news_list.append(news_item)

            except Exception as e:
                print(f"Ошибка парсинга новости: {e}")
                continue

        return news_list