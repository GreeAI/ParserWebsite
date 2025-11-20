import requests
import os


class VkBaseParser:
    def __init__(self, source_name):
        self.source_name = source_name
        self.access_token = os.getenv("VK_TOKEN")
        self.v = '5.199'
        self.count = 3 # последние новости с группы
        self.filter = 'owner'
        self.session = requests.Session()

    def parse(self):
        raise NotImplementedError("Not implemented")

    def get_page(self, url: str):
        """Запрос к VK API wall.get"""
        params = {
            'access_token': self.access_token,
            'v': self.v,
            'domain': self.source_name,
            'count': self.count,
            'filter': self.filter
        }
        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"Ошибка VK API: {data['error']}")
                return []

            return data.get("response", {}).get("items", [])
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
            return []