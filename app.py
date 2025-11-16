from flask import Flask, render_template, request, redirect, url_for, abort, make_response
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from functools import wraps
import atexit
import os
from dotenv import load_dotenv
from logs.logger import logging
from multiprocessing import current_process
from werkzeug.serving import is_running_from_reloader

from dataBase import NewsDatabase

# Парсеры
from parser.sibkray import SibkrayParser
# from parser.ngs_playwright import NGSPlaywrightParser
from parser.nsknews import NSKParser
# from parser.nsk_kp import NSKKPParser
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

# Инициализация
app = Flask(__name__)
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
db = NewsDatabase()

parsers = [
    SibkrayParser(), NSKParser(), SibFMParser(), KSParser(),
    VNParser(), NSKTVParser(), InfoProParser(), MKParser(),
    OMParser(), NDNParser(), NSKAIFParser(), ATASParser()
]

scheduler = BackgroundScheduler()

def start_scheduler():
    if current_process().name == "MainProcess" and not is_running_from_reloader():
        scheduler.add_job(func=parse_all_sites, trigger="interval", minutes=5)
        scheduler.start()
        atexit.register(lambda: db.close())
        logging.info("Планировщик запущен")

# Авторизация по токену
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token") or request.cookies.get("token")
        if token != ACCESS_TOKEN:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get("token")
        if token == ACCESS_TOKEN:
            resp = redirect(url_for('index'))
            resp.set_cookie("token", token, max_age=60*60*24*30)
            return resp
        return render_template("login.html", error="Неверный токен")
    return render_template("login.html")

@app.route('/')
@token_required
def index():
    page = request.args.get('page', 1, type=int)
    news = db.get_latest_news(count=10, page=page)
    total_pages = db.get_total_pages(per_page=10)

    template = 'page.html' if page > 1 else 'index.html'
    return render_template(template,
                           news=news,
                           current_page=page,
                           total_pages=total_pages,
                           total_news=db.get_news_count(),
                           now=datetime.now())

@app.route('/page/<int:page>')
@token_required
def news_page(page):
    if page < 1:
        page = 1

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

def parse_all_sites():
    logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск парсинга...")
    db.delete_old_news(hours=24)
    new_news_count = 0

    for parser in parsers:
        try:
            news_list = parser.parse()
            added = sum(1 for news in news_list if db.add_news(news))
            new_news_count += added
            logging.info(f"✅ {parser.source_name}: {len(news_list)} найдено, {added} новых")
        except Exception as e:
            logging.warning(f"❌ Ошибка в парсере {parser.source_name}: {e}")

    logging.info(f"Итого добавлено новых новостей: {new_news_count}")
    return new_news_count

if current_process().name == "MainProcess" and not is_running_from_reloader():
    parse_all_sites()
    start_scheduler()
