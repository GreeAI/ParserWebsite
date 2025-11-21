from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from logs.logger import logging
from dataBase import NewsDatabase
from config import VK_TOKEN

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
from parser.VK_ab_guardia import VKABGuardiaParser
from parser.VK_nsk_tv import VKNSKTVParser
from parser.VK_ots_gorsite import VKOtsGorSiteParser
from parser.VK_Sudi_Nsk import VKSudiNskParser
from parser.VK_precedent import VKPrecedentParser
from parser.telegram_parser import TelegramParser

db = NewsDatabase()

parsers = [
    SibkrayParser(), VKNSKTVParser(), NSKParser(), VKSudiNskParser(), SibFMParser(), KSParser(),
    VNParser(), VKABGuardiaParser(), NSKTVParser(), InfoProParser(), MKParser(), ATASParser(),
    OMParser(), VKOtsGorSiteParser(), NDNParser(), VKPrecedentParser(), NSKAIFParser(),TelegramParser()
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
