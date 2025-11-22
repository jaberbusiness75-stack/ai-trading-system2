import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    def __init__(self):
        # إعدادات التليجرام
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
        
        # إعدادات DeepSeek AI
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'YOUR_DEEPSEEK_API_KEY')
        self.DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
        
        # 🔑 مفاتيح API للبيانات الحقيقية
        self.TWELVEDATA_API_KEY = os.getenv('TWELVEDATA_API_KEY', 'demo')
        self.ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY', 'demo')
        
        # إعدادات MT5
        self.MT5_SERVER = os.getenv('MT5_SERVER', 'YourBrokerServer')
        self.MT5_LOGIN = int(os.getenv('MT5_LOGIN', '123456'))
        self.MT5_PASSWORD = os.getenv('MT5_PASSWORD', 'your_password')
        self.MT5_PATH = os.getenv('MT5_PATH', 'C:/Program Files/MetaTrader 5/terminal64.exe')
        
        # إعدادات المخاطرة
        self.RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', '0.03'))  # 3%
        self.MAX_DAILY_RISK = float(os.getenv('MAX_DAILY_RISK', '0.09'))  # 9%
        self.DEFAULT_BALANCE = float(os.getenv('DEFAULT_BALANCE', '10000.0'))
        
        # إعدادات التداول
        self.ENABLE_MT5_TRADING = os.getenv('ENABLE_MT5_TRADING', 'False').lower() == 'true'
        self.DEFAULT_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'USOIL']
        self.TRADING_SESSIONS = {
            'لندن': {'open': '08:00', 'close': '16:00'},
            'نيويورك': {'open': '13:00', 'close': '22:00'},
            'طوكيو': {'open': '00:00', 'close': '09:00'}
        }
        
        # إعدادات الأداء
        self.DATA_CACHE_TIMEOUT = int(os.getenv('DATA_CACHE_TIMEOUT', '300'))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

# إنشاء كائن الإعدادات
CONFIG = TradingConfig()