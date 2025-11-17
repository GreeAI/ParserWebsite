import sqlite3
import time
from models import NewsItem
from datetime import datetime


class NewsDatabase:
    def __init__(self, db_path='site.db'):
        self.db_path = db_path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)

    def _create_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS NewsItem (
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT,
                    created_at INTEGER NOT NULL
                )
            ''')
            conn.commit()

    def add_news(self, news_item):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO NewsItem (title, url, date, source, content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    news_item.title,
                    news_item.link,
                    news_item.date,
                    news_item.source,
                    news_item.content,
                    int(time.time())
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_latest_news(self, count=10, page=1):
        offset = (page - 1) * count
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, url, date, source, content, created_at
                FROM NewsItem
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (count, offset))
            rows = cursor.fetchall()
            return [NewsItem(*row[:5]) for row in rows]

    def get_news_count(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM NewsItem')
            return cursor.fetchone()[0]

    def get_total_pages(self, per_page=10):
        total = self.get_news_count()
        return (total + per_page - 1) // per_page

    def delete_old_news(self, hours=24):
        cutoff = int(time.time()) - hours * 3600
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM NewsItem WHERE created_at < ?', (cutoff,))
            conn.commit()

    def get_last_news_time(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(created_at) FROM news')
            row = cursor.fetchone()
            return datetime.fromtimestamp(row[0]) if row and row[0] else None
