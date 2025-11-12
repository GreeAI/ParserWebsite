from datetime import datetime
import json


class NewsItem:
    def __init__(self, title, link, date, source, content=""):
        self.title = title
        self.link = link
        self.date = date
        self.source = source
        self.content = content
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'date': self.date,
            'source': self.source,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        news = cls(
            title=data['title'],
            link=data['link'],
            date=data['date'],
            source=data['source'],
            content=data.get('content', '')
        )
        news.created_at = datetime.fromisoformat(data['created_at'])
        return news