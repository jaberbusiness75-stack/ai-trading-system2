import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.sessions = {
            'طوكيو': {'open': '00:00', 'close': '09:00', 'active': False},
            'لندن': {'open': '08:00', 'close': '16:00', 'active': False}, 
            'نيويورك': {'open': '13:00', 'close': '22:00', 'active': False}
        }
        logger.info("✅ تم تهيئة مدير الجلسات")

    def get_current_sessions(self):
        """الحصول على الجلسات النشطة حالياً"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            active_sessions = []
            
            # تحديث حالة الجلسات
            for session, times in self.sessions.items():
                open_hour = int(times['open'].split(':')[0])
                close_hour = int(times['close'].split(':')[0])
                
                is_active = open_hour <= current_hour < close_hour
                self.sessions[session]['active'] = is_active
                
                status = "🟢 نشطة" if is_active else "🔴 مغلقة"
                active_sessions.append(f"• {session}: {status} ({times['open']}-{times['close']} GMT)")
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"خطأ في جلب الجلسات: {e}")
            return ["❌ تعذر تحديد الجلسات النشطة"]

    def is_session_active(self, session_name: str) -> bool:
        """التحقق إذا كانت الجلسة نشطة"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            session = self.sessions.get(session_name)
            if session:
                open_hour = int(session['open'].split(':')[0])
                close_hour = int(session['close'].split(':')[0])
                return open_hour <= current_hour < close_hour
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الجلسة: {e}")
            return False

    def get_recommended_pairs(self):
        """الأزواج الموصى بها حسب الجلسة"""
        current_sessions = [session for session, data in self.sessions.items() if data['active']]
        
        if not current_sessions:
            return ["جميع الأزواج", "أوقات غير نشطة"]
        
        recommendations = {
            'لندن': ["EURUSD", "GBPUSD", "EURGBP", "GBPJPY"],
            'نيويورك': ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD"],
            'طوكيو': ["USDJPY", "EURJPY", "AUDJPY", "GBPJPY"]
        }
        
        pairs = []
        for session in current_sessions:
            pairs.extend(recommendations.get(session, []))
        
        return list(set(pairs))  # إزالة التكرارات