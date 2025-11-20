from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from functools import wraps
import os
from logs.logger import logging
from dataBase import NewsDatabase
from config import ACCESS_TOKEN
# Инициализация Flask
app = Flask(__name__)
db = NewsDatabase()

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
                           last_update=db.get_last_news_time()
                           )

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
                           last_update=db.get_last_news_time()
                           )
