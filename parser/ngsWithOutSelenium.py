import requests
from bs4 import BeautifulSoup
import re
from .baseParser import BaseParser
from models import NewsItem


class NGSFastParser(BaseParser):
    def __init__(self):
        super().__init__("НГС")
        self.url = "https://ngs.ru/text/"

    def parse(self):
        print("🚀 Запуск быстрого парсера NGS...")

        try:
            response = self.session.get(self.url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            news_list = []

            # Ищем новости по разным возможным селекторам
            selectors = [
                'div[class*="wrap"]',
                'article',
                '[data-news-item]',
                '.news-item'
            ]

            for selector in selectors:
                news_items = soup.select(selector)
                if news_items:
                    print(f"📊 Найдено элементов с селектором '{selector}': {len(news_items)}")

                    for item in news_items[:15]:  # Ограничиваем количество
                        try:
                            # Ищем заголовок и ссылку
                            title_elem = item.find('a', href=re.compile(r'/news/'))
                            if not title_elem:
                                continue

                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')

                            if not title or len(title) < 10:
                                continue

                            # Обрабатываем ссылку
                            if link and not link.startswith('http'):
                                link = 'https://ngs.ru' + link if link.startswith('/') else f'https://ngs.ru/{link}'

                            # Ищем дату
                            date = "Сегодня"
                            date_elem = item.find(['time', 'span'], class_=re.compile(r'time|date'))
                            if date_elem:
                                date = date_elem.get_text(strip=True)

                            news_item = NewsItem(
                                title=title,
                                link=link,
                                date=date,
                                source=self.source_name
                            )

                            # Проверяем дубликаты
                            if not any(n.link == link for n in news_list):
                                news_list.append(news_item)
                                print(f"✅ {title[:60]}...")

                        except Exception as e:
                            continue

                    if news_list:
                        break

            print(f"🎯 NGS: найдено {len(news_list)} уникальных новостей")
            return news_list

        except Exception as e:
            print(f"❌ Ошибка быстрого парсера NGS: {e}")
            return []