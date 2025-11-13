from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from models import NewsItem
from .baseParser import BaseParser
import logging
import os
import time


class NSKKPParser(BaseParser):
    def __init__(self):
        super().__init__("НКС КП")
        self.url = "https://www.nsk.kp.ru/online/"

        # Настройка логов
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, "kp_parser.log"),
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            encoding="utf-8"
        )

    def parse(self):
        logging.info("Запуск парсера КП Новосибирск...")
        news_list = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })

                for attempt in range(3):
                    try:
                        page.goto(self.url, timeout=60000, wait_until="domcontentloaded")

                        # Удаление всплывающих окон, если они мешают
                        page.evaluate("""
                            const selectors = ['.popup', '.overlay', '.banner', '[id*="cookie"]', '[class*="cookie"]'];
                            selectors.forEach(sel => {
                                const el = document.querySelector(sel);
                                if (el) el.remove();
                            });
                        """)

                        page.wait_for_selector("div.sc-1tputnk-12", timeout=15000, state="attached")
                        break
                    except Exception as e:
                        logging.warning(f"Попытка {attempt + 1} не удалась: {e}")
                        time.sleep(2)
                else:
                    logging.error("Не удалось загрузить страницу после 3 попыток.")
                    browser.close()
                    return []

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div.sc-1tputnk-12")

                for i, card in enumerate(cards[:15]):
                    try:
                        title_tag = card.select_one("a.sc-1tputnk-3")
                        title = title_tag.get_text(strip=True) if title_tag else ""
                        link = title_tag["href"] if title_tag else ""

                        if not title or not link:
                            continue

                        if not link.startswith("http"):
                            link = "https://www.nsk.kp.ru" + link

                        subtitle_tag = card.select_one("p")
                        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""

                        date_tag = card.select_one("time")
                        date = date_tag.get_text(strip=True) if date_tag else "Сегодня"

                        news_item = NewsItem(
                            title=title,
                            link=link,
                            date=date,
                            source=self.source_name,
                            content=subtitle
                        )
                        news_list.append(news_item)
                        logging.info(f"[{i + 1}] {title} — {link}")

                    except Exception as e:
                        logging.warning(f"Ошибка при обработке карточки {i + 1}: {e}")
                        continue

                browser.close()

        except Exception as e:
            logging.error(f"Ошибка Playwright: {e}")

        logging.info(f"Парсинг завершён. Найдено новостей: {len(news_list)}")
        return news_list
