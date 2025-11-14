import requests
from bs4 import BeautifulSoup
from models import NewsItem


class BaseParser:
    def __init__(self, source_name):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })

    def parse(self):
        raise NotImplementedError("Not implemented")

    def get_page(self, url):
        """Загрузка страницы"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
            return None