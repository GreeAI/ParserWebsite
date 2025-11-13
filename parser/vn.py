from .baseParser import BaseParser
from models import NewsItem


class VNParser(BaseParser):
    def __init__(self):
        super().__init__("ВН")
        self.url = "https://vn.ru/news/"

    def parse(self):
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        # Каждая новость — это article.section_news_item
        articles = soup.select('article.section_news_item')

        for article in articles:
            try:
                title_elem = article.select_one('h2.h2_section')
                link_elem = article.select_one('div.section_news_item_content_title a')
                date_elem = article.select_one('div.section_news_item_date span')
                description_elem = article.select_one('div.section_news_item_content_preview')

                if title_elem and link_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem["href"]
                    date = date_elem.get_text(strip=True)
                    description = description_elem.get_text(strip=True)

                    base_url = "https://vn.ru"
                    full_link = link if link.startswith("http") else f"{base_url}{link}"

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
