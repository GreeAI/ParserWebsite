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

        # Сначала пробуем новую верстку
        news_items = soup.select('ul.top-section__list li.top-section__item')
        if not news_items:
            # Если не нашли — fallback на старую верстку
            news_items = soup.select('div.top-block__last-news article.last-news__item')

        news_list = []

        for item in news_items:
            try:
                # --- Новый вариант ---
                title_elem = item.select_one('a.top-section-article__link')
                date_elem = item.select_one('span.item-footer__info')

                # --- Старый вариант ---
                if not title_elem:
                    title_elem = item.select_one('a.last-news__link')
                if not date_elem:
                    date_elems = item.select('span.last-news__date')
                    if len(date_elems) >= 2:
                        date_elem = date_elems[0]  # берём первую часть даты

                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem['href']
                date = date_elem.text.strip() if date_elem else "Сегодня"

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
