from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit
import os

from dataBase import NewsDatabase
from parser.sibkray import SibkrayParser
from parser.ngs import NGSSeleniumParser

app = Flask(__name__)
db = NewsDatabase()

# Инициализация парсеров
parsers = [
    SibkrayParser(),
    NGSSeleniumParser(),
]


def parse_all_sites():
    """Функция парсинга всех сайтов"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск парсинга...")

    new_news_count = 0

    for parser in parsers:
        try:
            print(f"Парсим {parser.source_name}...")
            news_list = parser.parse()

            added_count = 0
            for news in news_list:
                if db.add_news(news):
                    added_count += 1

            new_news_count += added_count
            print(f"✅ {parser.source_name}: {len(news_list)} найдено, {added_count} новых")

        except Exception as e:
            print(f"❌ Ошибка в парсере {parser.source_name}: {e}")

    print(f"Итого добавлено новых новостей: {new_news_count}")
    return new_news_count


# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(func=parse_all_sites, trigger="interval", minutes=5)
scheduler.start()

# Остановка планировщика при выходе
atexit.register(lambda: scheduler.shutdown())


@app.route('/api/news')
def api_news():
    """API для получения новостей"""
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    news = db.get_latest_news(count=count, page=page)
    news_data = [item.to_dict() for item in news]

    return jsonify({
        'news': news_data,
        'current_page': page,
        'total_pages': db.get_total_pages(per_page=count),
        'total_news': db.get_news_count()
    })


@app.route('/api/parse')
def api_parse():
    """Ручной запуск парсинга"""
    if request.args.get('key') != 'your_secret_key':  # Защита от случайных вызовов
        return jsonify({'error': 'Unauthorized'}), 401

    new_count = parse_all_sites()
    return jsonify({'new_news_added': new_count})


# Добавьте этот маршрут в app.py после существующих маршрутов

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    news = db.get_latest_news(count=10, page=page)
    total_pages = db.get_total_pages(per_page=10)

    if page > 1:
        return render_template('page.html',
                               news=news,
                               current_page=page,
                               total_pages=total_pages,
                               total_news=db.get_news_count(),
                               now=datetime.now())

    return render_template('index.html',
                           news=news,
                           current_page=page,
                           total_pages=total_pages,
                           total_news=db.get_news_count(),
                           now=datetime.now())


@app.route('/page/<int:page>')
def news_page(page):
    if page < 1:
        page = 1

    news = db.get_latest_news(count=10, page=page)
    total_pages = db.get_total_pages(per_page=10)

    if page > total_pages and total_pages > 0:
        page = total_pages
        news = db.get_latest_news(count=10, page=page)

    return render_template('page.html',
                           news=news,
                           current_page=page,
                           total_pages=total_pages,
                           total_news=db.get_news_count(),
                           now=datetime.now())


if __name__ == '__main__':
    # Первоначальный парсинг при запуске
    parse_all_sites()

    # Запуск Flask приложения
    app.run(host='0.0.0.0', port=5000, debug=True)