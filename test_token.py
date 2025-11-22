import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def test_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token or token == 'YOUR_TELEGRAM_BOT_TOKEN':
        print("❌ لم يتم تعيين TELEGRAM_BOT_TOKEN في ملف .env")
        print("🔧 يرجى إضافة سطر: TELEGRAM_BOT_TOKEN=رقم_التوكن_الحقيقي")
        return
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ البوت يعمل! اسم البوت: {me.first_name}")
        print(f"📞 اسم المستخدم: @{me.username}")
        
        # اختبار إرسال رسالة
        # await bot.send_message(chat_id=5486924120, text="🤖 البوت يعمل بنجاح!")
        # print("✅ تم إرسال رسالة اختبار")
        
    except Exception as e:
        print(f"❌ خطأ في التوكن: {e}")
        print("🔧 تأكد من:")
        print("1. التوكن صحيح")
        print("2. البوت مفعل في BotFather")
        print("3. لديك اتصال بالإنترنت")

if __name__ == "__main__":
    asyncio.run(test_bot())