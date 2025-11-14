from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit
from dataBase import NewsDatabase

from parser.sibkray import SibkrayParser
from parser.ngs_playwright import NGSPlaywrightParser
from parser.nsknews import NSKParser
from parser.nsk_kp import NSKKPParser
from parser.sibfm import SibFMParser
from parser.ks_online import KSParser
from parser.vn import VNParser
from parser.nsktv import NSKTVParser
from parser.infopro import InfoProParser
from parser.mkru import MKParser
from parser.om import OMParser
from parser.ndn import NDNParser
from parser.nsk_aif import NSKAIFParser
from parser.atas import ATASParser

app = Flask(__name__)
db = NewsDatabase()

# Инициализация парсеров
parsers = [
    SibkrayParser(),
    NGSPlaywrightParser(),
    NSKParser(),
    NSKKPParser(),
    SibFMParser(),
    KSParser(),
    VNParser(),
    NSKTVParser(),
    InfoProParser(),
    MKParser(),
    OMParser(),
    NDNParser(),
    NSKAIFParser(),
    ATASParser()
]


def parse_all_sites():
    """Функция парсинга всех сайтов"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск парсинга...")

    db.delete_old_news(hours=24)

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
atexit.register(lambda: db.close())

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
    # Защита от двойного запуска при debug=True
    from werkzeug.serving import is_running_from_reloader
    if not is_running_from_reloader():
        parse_all_sites()

    app.run(host='0.0.0.0', port=5000, debug=True)
