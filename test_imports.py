import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("🔍 اختبار استيراد المكونات...")

try:
    from config import CONFIG
    print("✅ config.py - OK")
except Exception as e:
    print(f"❌ config.py - FAILED: {e}")

try:
    from data_provider import DataProvider
    print("✅ data_provider.py - OK")
except Exception as e:
    print(f"❌ data_provider.py - FAILED: {e}")

try:
    from telegram_bot import TradingBot
    print("✅ telegram_bot.py - OK")
except Exception as e:
    print(f"❌ telegram_bot.py - FAILED: {e}")

print("🎯 جاهز للتشغيل...")