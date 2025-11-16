from .baseParser import BaseParser
from models import NewsItem
from logs.logger import logging


class KSParser(BaseParser):
    def __init__(self):
        super().__init__("КС Онлайн")
        self.url = "https://ksonline.ru/"

    def parse(self):
        logging.info("Запуск парсера КС Онлайн")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        news_links = soup.select('a.current')

        for link_elem in news_links:
            try:
                title_elem = link_elem.select_one('p.wnews')
                date_elem = link_elem.select_one('code.post-item-clock')

                if title_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem["href"]
                    date = date_elem.get_text(strip=True)

                    news_item = NewsItem(
                        title=title,
                        link=link,
                        date=date,
                        source=self.source_name
                    )
                    news_list.append(news_item)

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list