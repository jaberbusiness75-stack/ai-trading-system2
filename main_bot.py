import logging
import sys
import os
from datetime import datetime
import time
from keep_alive import keep_alive

# 🔧 تشغيل خادم Keep-Alive
keep_alive()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('trading_bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """معالج الاستثناءات العالمي"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("❌ خطأ غير معالج:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

def print_banner():
    banner = """
🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯
🤖 نظام التداول الآلي الذكي - الإصدار السحابي
☁️  يعمل 24/7 على الاستضافة السحابية
🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯
"""
    print(banner)

def main():
    """الدالة الرئيسية مع إعادة التشغيل التلقائي"""
    max_retries = 5
    retry_delay = 30  # ثواني
    
    for attempt in range(max_retries):
        try:
            print_banner()
            print(f"🔄 محاولة التشغيل {attempt + 1}/{max_retries}")
            
            from telegram_bot import TradingBot
            
            bot = TradingBot()
            print("🎯 البوت يعمل بنجاح على السحابة! ☁️")
            bot.run()
            
        except Exception as e:
            print(f"❌ فشلت المحاولة {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ إعادة المحاولة خلال {retry_delay} ثانية...")
                time.sleep(retry_delay)
                retry_delay *= 2  # زيادة وقت الانتظار
            else:
                print("❌ فشلت جميع محاولات التشغيل")
                raise

if __name__ == "__main__":
    main()