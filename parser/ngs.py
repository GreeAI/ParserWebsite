from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .baseParser import BaseParser
from models import NewsItem


class NGSSeleniumParser(BaseParser):
    def __init__(self):
        super().__init__("НГС")
        self.url = "https://ngs.ru/text/"

    def parse(self):
        print("Запуск Selenium парсера для NGS...")

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Добавляем User-Agent для Selenium
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(options=options)
        news_list = []

        try:
            driver.get(self.url)
            print("Страница загружается...")

            # Ждем загрузки контента
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.wrap_RL97A')))

            # Даем дополнительное время для полной загрузки
            time.sleep(3)

            # Ищем все карточки новостей
            news_cards = driver.find_elements(By.CSS_SELECTOR, 'div.wrap_RL97A')
            print(f"Найдено карточек: {len(news_cards)}")

            for i, card in enumerate(news_cards[:15]):  # Ограничиваем количество
                try:
                    print(f"Обрабатываем карточку {i + 1}...")

                    # Заголовок и ссылка
                    title_element = card.find_element(By.CSS_SELECTOR, 'a.header_RL97A')
                    title = title_element.text.strip()
                    link = title_element.get_attribute('href')

                    if not title:
                        continue

                    # Подзаголовок/описание
                    try:
                        subtitle_element = card.find_element(By.CSS_SELECTOR, 'span.subtitle_RL97A')
                        subtitle = subtitle_element.text.strip()
                    except:
                        subtitle = ""

                    # Дата
                    date = self._extract_date(card)

                    # Создаем объект новости
                    news_item = NewsItem(
                        title=title,
                        link=link,
                        date=date,
                        source=self.source_name,
                        content=subtitle
                    )

                    news_list.append(news_item)
                    print(f"✓ Добавлена новость: {title[:60]}...")

                except Exception as e:
                    print(f"✗ Ошибка при парсинге карточки {i + 1}: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при работе Selenium: {e}")
        finally:
            driver.quit()

        print(f"Selenium парсер NGS завершил работу. Найдено новостей: {len(news_list)}")
        return news_list

    def _extract_date(self, card):
        """Извлечение даты из карточки"""
        date_selectors = [
            'span.text_eIDCU',
            '.statistic_RL97A span',
            '.wrap_eIDCU span',
            '[class*="time"]',
            '[class*="date"]'
        ]

        for selector in date_selectors:
            try:
                date_elements = card.find_elements(By.CSS_SELECTOR, selector)
                for date_element in date_elements:
                    date_text = date_element.text.strip()
                    if date_text and any(char.isdigit() for char in date_text):
                        return date_text
            except:
                continue

        return "Сегодня"