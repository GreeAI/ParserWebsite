from .baseParser import BaseParser
from models import NewsItem
from logs.logger import logging


class SibkrayParser(BaseParser):
    def __init__(self):
        super().__init__("Сибирский Край")
        self.url = "https://sibkray.ru"

    def parse(self):
        logging.info("Запуск парсера Сибирский Край")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_items = soup.select('div.top-block__last-news article.last-news__item')
        news_list = []

        for item in news_items:
            try:
                title_elem = item.select_one('a.last-news__link')
                date_elems = item.select('span.last-news__date')

                if title_elem and len(date_elems) >= 2:
                    title = title_elem.text.strip()
                    link = title_elem['href']
                    date = f"{date_elems[0].text.strip()} {date_elems[1].text.strip()}"

                    news_item = NewsItem(
                        title=title,
                        link=link if link.startswith('http') else f"{self.url}{link}",
                        date=date,
                        source=self.source_name
                    )
                    news_list.append(news_item)

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list