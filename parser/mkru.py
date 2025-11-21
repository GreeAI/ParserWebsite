from .baseParser import BaseParser
from models import NewsItem
from logs.logger import logging

class MKParser(BaseParser):
    def __init__(self):
        super().__init__("МК Ру")
        self.url = "https://novos.mk.ru/news/"

    def parse(self):
        logging.info("Запуск парсера МК Ру")
        soup = self.get_page(self.url)
        if not soup:
            return []

        news_list = []

        # пробуем новую верстку
        sections = soup.select('section.news-listing__day-group')
        if not sections:
            # fallback на старую верстку
            sections = soup.select('div.news-listing')

        for section in sections:
            try:
                # дата дня
                date_elem = section.select_one('h2.news-listing__day-date')
                if not date_elem:
                    date_elem = section.select_one('div.news-date')
                date = date_elem.get_text(strip=True) if date_elem else ""

                # список новостей
                news_items = section.select('li.news-listing__item')
                if not news_items:
                    news_items = section.select('div.news-item')

                for item in news_items:
                    # --- новый вариант ---
                    title_elem = item.select_one('h3.news-listing__item-title')
                    link_elem = item.select_one('a.news-listing__item-link')
                    time_elem = item.select_one('span.news-listing__item-time')

                    # --- fallback ---
                    if not title_elem:
                        title_elem = item.select_one('a.news-title')
                    if not link_elem:
                        link_elem = item.select_one('a')
                    if not time_elem:
                        time_elem = item.select_one('span.news-time')

                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get("href", "").strip()
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

                        if len(news_list) >= 20:  # можно увеличить лимит
                            break

            except Exception as e:
                logging.warning(f"Ошибка парсинга новости: {e}")
                continue

        return news_list
