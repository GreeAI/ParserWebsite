from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from logs.logger import logging
from dataBase import NewsDatabase

# Парсеры
from parser.sibkray import SibkrayParser
from parser.nsknews import NSKParser
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

db = NewsDatabase()

parsers = [
    SibkrayParser(), NSKParser(), SibFMParser(), KSParser(),
    VNParser(), NSKTVParser(), InfoProParser(), MKParser(),
    OMParser(), NDNParser(), NSKAIFParser(), ATASParser()
]

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

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(parse_all_sites, "interval", minutes=5)
    logging.info("Планировщик запущен")
    scheduler.start()
