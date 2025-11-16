from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from models import NewsItem
from .baseParser import BaseParser
import time
import logging


class NGSPlaywrightParser(BaseParser):
    def __init__(self):
        super().__init__("НГС")
        self.url = "https://ngs.ru/text/"

    def parse(self):
        logging.info("Запуск Playwright парсера для NGS...")
        news_list = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })

                # Повторные попытки загрузки
                for attempt in range(3):
                    try:
                        page.goto(self.url, timeout=60000)
                        page.wait_for_selector("div.wrap_RL97A", timeout=15000)
                        break
                    except Exception as e:
                        logging.warning(f"Попытка {attempt + 1} не удалась: {e}")
                        time.sleep(3)
                else:
                    logging.error("Не удалось загрузить страницу после 3 попыток.")
                    browser.close()
                    return []

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div.wrap_RL97A")

                for i, card in enumerate(cards[:15]):
                    try:
                        title_tag = card.select_one("a.header_RL97A")
                        subtitle_tag = card.select_one("span.subtitle_RL97A")

                        title = title_tag.get_text(strip=True) if title_tag else ""
                        link = title_tag["href"] if title_tag else ""
                        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""
                        date = self._extract_date(card)

                        if not title or not link:
                            continue

                        news_item = NewsItem(
                            title=title,
                            link=link,
                            date=date,
                            source=self.source_name,
                            content=subtitle
                        )
                        news_list.append(news_item)
                        logging.info(f"[{i+1}] {title} — {link}")

                    except Exception as e:
                        logging.warning(f"Ошибка при обработке карточки {i+1}: {e}")
                        continue

                browser.close()

        except Exception as e:
            logging.error(f"❌ Ошибка Playwright: {e}")

        logging.info(f"Парсинг завершён. Найдено новостей: {len(news_list)}")
        return news_list

    def _extract_date(self, card):
        """Извлечение даты и времени из карточки"""
        date_selectors = [
            'span.text_eIDCU',
            '.statistic_RL97A span',
            '.wrap_eIDCU span',
            '[class*="time"]',
            '[class*="date"]'
        ]

        for selector in date_selectors:
            date_elements = card.select(selector)
            for date_element in date_elements:
                date_text = date_element.get_text(strip=True)
                if date_text and any(char.isdigit() for char in date_text):
                    return date_text

        return "Сегодня"
