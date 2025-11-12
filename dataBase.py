import json
import os
from datetime import datetime
from models import NewsItem


class NewsDatabase:
    def __init__(self, db_file='news_db.json'):
        self.db_file = db_file
        self.news = []
        self.load_data()

    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.news = [NewsItem.from_dict(item) for item in data]
            except Exception as e:
                print(f"Ошибка загрузки БД: {e}")
                self.news = []

    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                data = [news.to_dict() for news in self.news]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения БД: {e}")

    def add_news(self, news_item):
        """Добавление новости (если она новая)"""
        # Проверяем, есть ли уже такая новость
        for existing_news in self.news:
            if existing_news.link == news_item.link:
                return False

        # Добавляем в начало списка
        self.news.insert(0, news_item)

        # Сохраняем изменения
        self.save_data()
        return True

    def get_latest_news(self, count=10, page=1):
        """Получение последних новостей с пагинацией"""
        start_idx = (page - 1) * count
        end_idx = start_idx + count
        return self.news[start_idx:end_idx]

    def get_total_pages(self, per_page=10):
        """Получение общего количества страниц"""
        return (len(self.news) + per_page - 1) // per_page

    def get_news_count(self):
        """Получение общего количества новостей"""
        return len(self.news)