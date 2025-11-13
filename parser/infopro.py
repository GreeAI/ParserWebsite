from .baseParser import BaseParser
from models import NewsItem


class InfoProParser(BaseParser):
    def __init__(self):
        super().__init__("Инфо Про 54")
        self.url = "https://infopro54.ru/allnews/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        posts = soup.select('div.dslc-post')  # Каждая новость

        for post in posts:
            try:
                title_elem = post.select_one('div.dslc-blog-post-title h2 a')
                date_elem = post.select_one('div.dslc-blog-post-meta-date')

                if title_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem["href"]
                    date = date_elem.get_text(strip=True)

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
