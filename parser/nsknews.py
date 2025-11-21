from .baseParser import BaseParser
from models import NewsItem
from logs.logger import logging

class NSKParser(BaseParser):
    def __init__(self):
        super().__init__("НСК Новости")
        self.url = "https://nsknews.info/news"

    def parse(self):
        logging.info("Запуск парсера НСК Новости")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_items = soup.select('div.nn-news-article-hor')
        news_list = []

        for item in news_items:
            try:
                # --- Новый вариант верстки ---
                title_elem = item.select_one('.nn-materials-header_hidden_name a')
                date_elem = item.select_one('.nn-news-article-hor__date')

                # --- Старый вариант верстки ---
                if not title_elem:
                    title_elem = item.select_one('a')
                if not date_elem:
                    date_elem = item.select_one('span.last-news__date')

                # --- Заголовок ---
                title = title_elem.text.strip() if title_elem else ""
                link = title_elem.get('href', '').strip() if title_elem else ""
                date = date_elem.text.strip() if date_elem else "Сегодня"

                if not title or not link:
                    continue

                base_url = "https://nsknews.info"
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
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list
