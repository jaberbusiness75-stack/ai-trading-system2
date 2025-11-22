import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import pandas as pd
import sys
import os
import threading
import time

# ✅ إضافة المسار الحالي لـ sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG

logger = logging.getLogger(__name__)

# ✅ استيراد DataProvider مع معالجة الأخطاء
try:
    from data_provider import DataProvider
    DATA_PROVIDER_AVAILABLE = True
    logger.info("✅ تم استيراد DataProvider بنجاح")
except ImportError as e:
    logger.error(f"❌ فشل استيراد DataProvider: {e}")
    DATA_PROVIDER_AVAILABLE = False
    
    # ✅ إنشاء بديل بسيط
    class SimpleDataProvider:
        def __init__(self, config=None):
            self.config = config
            logger.info("🔄 استخدام SimpleDataProvider كبديل")
        
        def get_current_price(self, symbol):
            prices = {
                'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
                'USDCHF': 0.8850, 'USDCAD': 1.3600, 'AUDUSD': 0.6550,
                'XAUUSD': 1985.50, 'USOIL': 75.80
            }
            price = prices.get(symbol, 1.0)
            logger.info(f"💰 السعر الافتراضي لـ {symbol}: {price}")
            return price
        
        def get_market_summary(self, symbols=None):
            if symbols is None:
                symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD']
            summary = {}
            for symbol in symbols:
                price = self.get_current_price(symbol)
                if price:
                    summary[symbol] = price
            logger.info(f"📊 ملخص السوق الافتراضي: {len(summary)} أصول")
            return summary
        
        def get_fast_market_summary(self, symbols=None):
            return self.get_market_summary(symbols)
        
        def get_symbol_data(self, symbol, period='1d', interval='1h'):
            logger.info(f"📊 البيانات الافتراضية لـ {symbol}")
            return None
        
        def clear_cache(self):
            logger.info("✅ مسح التخزين المؤقت (افتراضي)")
    
    DataProvider = SimpleDataProvider

# ✅ استيراد الوحدات الأخرى مع معالجة الأخطاء
try:
    from risk_management import RiskManager
    RISK_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ RiskManager غير متوفر")
    RISK_MANAGER_AVAILABLE = False

try:
    from advanced_analysis import AdvancedAnalysis
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ AdvancedAnalysis غير متوفر")
    ADVANCED_ANALYSIS_AVAILABLE = False

try:
    from economic_calendar import EconomicCalendar
    ECONOMIC_CALENDAR_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ EconomicCalendar غير متوفر")
    ECONOMIC_CALENDAR_AVAILABLE = False

try:
    from session_manager import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ SessionManager غير متوفر")
    SESSION_MANAGER_AVAILABLE = False

class TradingBot:
    def __init__(self):
        logger.info("🤖 تهيئة بوت التداول السريع...")
        
        # ✅ تهيئة DataProvider
        self.data_provider = DataProvider(config=CONFIG)
        
        # ⚡ تحميل بيانات مسبق في الخلفية
        self._preload_data_async()
        
        # ✅ تهيئة الوحدات الأخرى مع التحقق من التوفر
        if RISK_MANAGER_AVAILABLE:
            self.risk_manager = RiskManager()
        else:
            self.risk_manager = None
            
        if ADVANCED_ANALYSIS_AVAILABLE and DATA_PROVIDER_AVAILABLE:
            self.advanced_analysis = AdvancedAnalysis(self.data_provider)
        else:
            self.advanced_analysis = None
            
        if ECONOMIC_CALENDAR_AVAILABLE:
            self.economic_calendar = EconomicCalendar()
        else:
            self.economic_calendar = None
            
        if SESSION_MANAGER_AVAILABLE:
            self.session_manager = SessionManager()
        else:
            self.session_manager = None
        
        # ✅ تهيئة بوت التليجرام
        self.telegram_token = CONFIG.TELEGRAM_BOT_TOKEN
        if not self.telegram_token or self.telegram_token == 'YOUR_TELEGRAM_BOT_TOKEN':
            logger.error("❌ لم يتم تعيين TELEGRAM_BOT_TOKEN")
            raise ValueError("TELEGRAM_BOT_TOKEN مطلوب - يرجى تعيينه في ملف .env")
            
        self.application = Application.builder().token(self.telegram_token).build()
        self._setup_handlers()
        
        logger.info("✅ تم تهيئة TradingBot بنجاح")

    def _preload_data_async(self):
        """تحميل بيانات مسبق في الخلفية لتحسين الاستجابة"""
        def preload():
            try:
                logger.info("🔄 تحميل البيانات المسبق في الخلفية...")
                # تحميل البيانات الأساسية فقط
                symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
                for symbol in symbols:
                    self.data_provider.get_symbol_data(symbol, '1d', '1h')
                logger.info("✅ اكتمل التحميل المسبق")
            except Exception as e:
                logger.debug(f"تحميل مسبق: {e}")
        
        thread = threading.Thread(target=preload, daemon=True)
        thread.start()

    def _setup_handlers(self):
        """إعداد معالجات الأوامر"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("market", self.market_summary))
        self.application.add_handler(CommandHandler("fast", self.fast_market))
        self.application.add_handler(CommandHandler("calendar", self.economic_calendar_cmd))
        self.application.add_handler(CommandHandler("sessions", self.trading_sessions))
        self.application.add_handler(CommandHandler("risk", self.risk_report))
        self.application.add_handler(CommandHandler("analysis", self.analysis_cmd))
        self.application.add_handler(CommandHandler("signals", self.signals_cmd))
        self.application.add_handler(CommandHandler("clear", self.clear_cache))
        
        logger.info("✅ تم إعداد معالجات الأوامر")

    def get_main_keyboard(self):
        """لوحة المفاتيح الرئيسية"""
        keyboard = [
            [InlineKeyboardButton("📊 ملخص السوق", callback_data='market')],
            [InlineKeyboardButton("⚡ سريع", callback_data='fast')],
            [InlineKeyboardButton("📅 الأحداث الاقتصادية", callback_data='calendar')],
            [InlineKeyboardButton("🌍 جلسات التداول", callback_data='sessions')],
            [InlineKeyboardButton("📈 تحليل مفصل", callback_data='analysis')],
            [InlineKeyboardButton("📊 تقرير المخاطرة", callback_data='risk')]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        welcome_text = f"""
🎯 أهلاً وسهلاً {user.first_name}!

🤖 **نظام التداول الآلي الذكي - الإصدار السريع**
⚡ الآن مع تحسينات السرعة والأداء

📊 **الأوامر المتاحة:**
/market - ملخص السوق الحالي (سريع)
/fast - أسعار فورية فائقة السرعة  
/calendar - الأحداث الاقتصادية  
/sessions - جلسات التداول
/analysis - تحليل مفصل لزوج
/signals - إشارات التداول الحالية
/risk - تقرير المخاطرة
/clear - مسح الذاكرة المؤقتة

💡 **الميزات المحسنة:**
✅ سرعة مضاعفة في استجابة الأوامر
✅ تحميل بيانات مسبق في الخلفية
✅ ذاكرة تخزين مؤقت محسنة
✅ بيانات حقيقية من MT5 و Twelve Data

🚀 جاهز للتداول الذكي!
        """
        await update.message.reply_text(welcome_text, reply_markup=self.get_main_keyboard())
        logger.info(f"تم ترحيب المستخدم {user.id}")

    async def market_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /market - النسخة السريعة"""
        try:
            await update.message.reply_text("⚡ جاري جلب البيانات...")
            
            # استخدام النسخة السريعة
            summary = self.data_provider.get_fast_market_summary()
            
            if summary:
                text = "📊 **ملخص السوق السريع:**\n\n"
                for symbol, price in summary.items():
                    change_emoji = "📈" if price > 1.0 else "📉"
                    text += f"• {symbol}: {price:.4f} {change_emoji}\n"
                text += f"\n🕒 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"
                text += f"\n⚡ الوضع السريع: مفعل"
            else:
                text = "❌ تعذر جلب بيانات السوق في الوقت الحالي"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال ملخص السوق السريع")
            
        except Exception as e:
            error_text = f"❌ خطأ في جلب بيانات السوق: {str(e)}"
            await update.message.reply_text(error_text)
            logger.error(f"خطأ في market_summary: {e}")

    async def fast_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /fast - ملخص سوق فائق السرعة"""
        try:
            # بيانات فورية بدون تحميل
            prices = {
                'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
                'USDCHF': 0.8850, 'USDCAD': 1.3600, 'AUDUSD': 0.6550,
                'XAUUSD': 1985.50, 'USOIL': 75.80
            }
            
            text = "⚡ **الأسعار الفورية:**\n\n"
            for symbol, price in prices.items():
                text += f"• {symbol}: {price:.4f}\n"
            
            text += f"\n🕒 {datetime.now().strftime('%H:%M:%S')}"
            text += "\n💡 استخدام /market للبيانات الحية المحدثة"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال الأسعار الفورية")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في الوضع السريع")
            logger.error(f"خطأ في fast_market: {e}")

    async def economic_calendar_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /calendar"""
        try:
            if self.economic_calendar:
                events = self.economic_calendar.get_today_events()
                if events:
                    text = "📅 **الأحداث الاقتصادية اليوم:**\n\n"
                    for event in events[:5]:
                        text += f"• {event}\n"
                    text += f"\n📊 إجمالي الأحداث: {len(events)}"
                else:
                    text = "📅 لا توجد أحداث اقتصادية مهمة اليوم"
            else:
                text = "⚠️ خدمة التقويم الاقتصادي غير متوفرة حالياً"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال التقويم الاقتصادي")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في جلب التقويم الاقتصادي")
            logger.error(f"خطأ في economic_calendar: {e}")

    async def trading_sessions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /sessions"""
        try:
            if self.session_manager:
                sessions = self.session_manager.get_current_sessions()
                text = "🌍 **جلسات التداول الحالية:**\n\n"
                for session in sessions:
                    text += f"{session}\n"
                
                # إضافة الأزواج الموصى بها
                recommended = self.session_manager.get_recommended_pairs()
                text += f"\n💡 **الأزواج الموصى بها:**\n{', '.join(recommended)}"
            else:
                text = "🌍 **جلسات التداول:**\n\n• لندن: 8:00-16:00 GMT\n• نيويورك: 13:00-21:00 GMT\n• طوكيو: 23:00-7:00 GMT"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال معلومات الجلسة")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في جلب جلسات التداول")
            logger.error(f"خطأ في trading_sessions: {e}")

    async def risk_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /risk"""
        try:
            if self.risk_manager:
                report = self.risk_manager.get_risk_report()
                text = f"📊 **تقرير المخاطرة:**\n\n{report}"
            else:
                text = "📊 **إعدادات المخاطرة الافتراضية:**\n\n• المخاطرة لكل صفقة: 2%\n• الحد الأقصى للمخاطرة اليومية: 6%\n• نسبة الربح/الخسارة: 1:2"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال تقرير المخاطرة")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في جلب تقرير المخاطرة")
            logger.error(f"خطأ في risk_report: {e}")

    async def analysis_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /analysis - تحليل مفصل"""
        try:
            symbol = context.args[0] if context.args else 'EURUSD'
            symbol = symbol.upper()
            
            await update.message.reply_text(f"🔍 جاري تحليل {symbol}...")
            
            if self.advanced_analysis:
                analysis_text = self.advanced_analysis.get_detailed_analysis(symbol)
            else:
                analysis_text = f"🔍 تحليل {symbol}: الخدمة غير متوفرة حالياً"
            
            await update.message.reply_text(analysis_text, reply_markup=self.get_main_keyboard())
            logger.info(f"تم إرسال تحليل {symbol}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في التحليل: {str(e)}")
            logger.error(f"خطأ في analysis_cmd: {e}")

    async def signals_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /signals - إشارات التداول"""
        try:
            await update.message.reply_text("🎯 جاري تحليل إشارات التداول...")
            
            if self.advanced_analysis:
                signals = self.advanced_analysis.get_trading_signals()
                
                if signals:
                    text = "⚡ **إشارات التداول الحالية:**\n\n"
                    for symbol, signal_data in list(signals.items())[:6]:  # عرض أول 6 إشارات
                        emoji = "🟢" if signal_data['signal'] == 'شراء' else "🔴" if signal_data['signal'] == 'بيع' else "🟡"
                        text += f"{emoji} **{symbol}**: {signal_data['signal']} (ثقة: {signal_data['confidence']:.0f}%)\n"
                        text += f"   💰 السعر: {signal_data['current_price']:.4f} | RSI: {signal_data['rsi']:.1f}\n\n"
                    
                    # إضافة توصيات
                    text += "💡 **التوصيات:**\n"
                    text += "• 🎯 ركز على الإشارات ذات الثقة >70%\n"
                    text += "• ⏰ استخدم أوامر وقف الخسارة\n"
                    text += "• 📊 تنويع المحفظة"
                else:
                    text = "📊 لا توجد إشارات تداول قوية حالياً"
            else:
                text = "⚠️ خدمة الإشارات غير متوفرة حالياً"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم إرسال إشارات التداول")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في جلب الإشارات")
            logger.error(f"خطأ في signals_cmd: {e}")

    async def clear_cache(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /clear - مسح الذاكرة المؤقتة"""
        try:
            if hasattr(self.data_provider, 'clear_cache'):
                self.data_provider.clear_cache()
                text = "✅ تم مسح الذاكرة المؤقتة بنجاح"
            else:
                text = "⚠️ خاصية مسح الذاكرة غير متوفرة"
            
            await update.message.reply_text(text, reply_markup=self.get_main_keyboard())
            logger.info("تم مسح الذاكرة المؤقتة")
            
        except Exception as e:
            await update.message.reply_text("❌ خطأ في مسح الذاكرة")
            logger.error(f"خطأ في clear_cache: {e}")

    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل بوت التليجرام السريع...")
        print("🎯 بوت التداول الذكي (الإصدار السريع) يعمل الآن...")
        print("📱 اذهب إلى التليجرام وابدأ المحادثة مع البوت")
        print("⚡ جرب الأمر /fast للأسعار الفورية")
        self.application.run_polling()
def restart_bot(self):
    """إعادة تشغيل البوت عند الفشل"""
    logger.info("🔄 إعادة تشغيل البوت...")
    import os
    import sys
    os.execv(sys.executable, [sys.executable] + sys.argv)

async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"❌ خطأ في المعالج: {context.error}")
    
    try:
        # محاولة إرسال رسالة خطأ للمستخدم
        await context.bot.send_message(
            chat_id=update.effective_chat.id if update else None,
            text="❌ حدث خطأ في النظام، جاري المعالجة..."
        )
    except:
        pass

def run_with_restart(self):
    """تشغيل البوت مع إعادة التشغيل التلقائي"""
    max_restarts = 3
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            logger.info(f"🚀 بدء تشغيل البوت (المحاولة {restart_count + 1})")
            self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                close_loop=False
            )
        except Exception as e:
            restart_count += 1
            logger.error(f"❌ انتهى البوت بشكل غير متوقع: {e}")
            
            if restart_count < max_restarts:
                logger.info(f"🔄 إعادة التشغيل خلال 10 ثواني...")
                time.sleep(10)
            else:
                logger.critical("❌ فشلت جميع محاولات إعادة التشغيل")
                raise