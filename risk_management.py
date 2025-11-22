import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, initial_balance=10000.0):
        self.account_balance = initial_balance
        self.risk_per_trade = 0.03  # 3% لكل صفقة
        self.max_daily_risk = 0.09  # 9% حد يومي
        self.daily_loss_limit = initial_balance * self.max_daily_risk
        self.today_losses = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        logger.info(f"تهيئة RiskManager برصيد: ${initial_balance}")

    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        """حجم المركز بناء على وقف الخسارة"""
        try:
            risk_amount = self.account_balance * self.risk_per_trade
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                return 0.0
                
            position_size = risk_amount / price_diff
            logger.info(f"حجم المركز لـ {symbol}: {position_size:.2f} (خطر: ${risk_amount:.2f})")
            return position_size
            
        except Exception as e:
            logger.error(f"خطأ في حساب حجم المركز: {e}")
            return 0.0

    def validate_trade(self, symbol: str, position_size: float, trade_type: str) -> bool:
        """التحقق من صحة الصفقة"""
        try:
            # التحقق من الحد اليومي
            if self.today_losses >= self.daily_loss_limit:
                logger.warning("❌ تم الوصول للحد اليومي للخسائر")
                return False
            
            # التحقق من حجم المركز
            max_position = self.account_balance * 0.1  # 10% كحد أقصى للمركز
            if position_size > max_position:
                logger.warning(f"❌ حجم المركز يتجاوز الحد المسموح: {position_size:.2f} > {max_position:.2f}")
                return False
            
            logger.info(f"✅ الصفقة مقبولة لـ {symbol} - حجم: {position_size:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصفقة: {e}")
            return False

    def update_trade_result(self, profit_loss: float):
        """تحديث نتيجة الصفقة"""
        self.total_trades += 1
        self.today_losses += max(0, -profit_loss)  # إضافة الخسائر فقط
        
        if profit_loss > 0:
            self.winning_trades += 1
            
        logger.info(f"تم تحديث نتيجة الصفقة: ${profit_loss:.2f} (إجمالي اليوم: ${self.today_losses:.2f})")

    def get_risk_report(self) -> str:
        """تقرير المخاطرة"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        report = f"""
📊 **تقرير إدارة المخاطرة:**

💰 **الحساب:**
• الرصيد الحالي: ${self.account_balance:,.2f}
• إجمالي الصفقات: {self.total_trades}
• نسبة الصفقات الرابحة: {win_rate:.1f}%

🎯 **مستويات المخاطرة:**
• المخاطرة لكل صفقة: {self.risk_per_trade * 100}% (${self.account_balance * self.risk_per_trade:,.2f})
• الحد اليومي للخسائر: {self.max_daily_risk * 100}% (${self.daily_loss_limit:,.2f})
• الخسائر اليومية: ${self.today_losses:,.2f}

⚡ **الحالة الحالية:**
• الصفقات المتبقية اليوم: {int((self.daily_loss_limit - self.today_losses) / (self.account_balance * self.risk_per_trade))}
• الحالة: {'🟢 نشط' if self.today_losses < self.daily_loss_limit else '🔴 متوقف'}

📈 **التوصيات:**
• حجم المركز الأمثل: ${self.account_balance * 0.03:,.2f}
• نسبة الربح/الخسارة الموصى بها: 1:2
• أقصى رافعة مالية موصى بها: 1:10
        """
        return report

    def set_account_balance(self, new_balance: float):
        """تحديث رصيد الحساب"""
        self.account_balance = new_balance
        self.daily_loss_limit = new_balance * self.max_daily_risk
        logger.info(f"تم تحديث الرصيد: ${new_balance:,.2f}")

    def reset_daily_losses(self):
        """إعادة تعيين الخسائر اليومية"""
        self.today_losses = 0.0
        logger.info("✅ تم إعادة تعيين الخسائر اليومية")