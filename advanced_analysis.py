import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedAnalysis:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.signals_history = []
        logger.info("✅ تم تهيئة نظام التحليل المتقدم")
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """تحليل رمز معين بشكل متقدم"""
        try:
            data = self.data_provider.get_symbol_data(symbol, period='3mo', interval='4h')
            
            if data is None or data.empty:
                return {"error": f"لا توجد بيانات لـ {symbol}"}
            
            current_price = data['Close'].iloc[-1]
            
            # حساب المؤشرات المتقدمة
            ma20 = data['Close'].rolling(20).mean().iloc[-1]
            ma50 = data['Close'].rolling(50).mean().iloc[-1]
            ma200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else ma50
            
            # RSI
            rsi = self._calculate_rsi(data['Close']).iloc[-1] if 'RSI' not in data else data['RSI'].iloc[-1]
            
            # تقلبات
            volatility = data['Close'].pct_change().std() * np.sqrt(252)  # التقلب السنوي
            
            # دعم ومقاومة
            support, resistance = self._calculate_support_resistance(data)
            
            # تحديد الاتجاه والقوة
            trend, trend_strength = self._determine_trend(data, ma20, ma50, ma200)
            
            # توليد الإشارة
            signal, confidence = self._generate_signal(data, current_price, ma20, ma50, rsi, support, resistance)
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'trend': trend,
                'trend_strength': trend_strength,
                'signal': signal,
                'confidence': confidence,
                'rsi': rsi,
                'ma20': ma20,
                'ma50': ma50,
                'ma200': ma200,
                'support': support,
                'resistance': resistance,
                'volatility': volatility,
                'timestamp': datetime.now()
            }
            
            # حفظ الإشارة في السجل
            if confidence > 60:  # فقط الإشارات ذات الثقة العالية
                self.signals_history.append(analysis)
                logger.info(f"🎯 إشارة لـ {symbol}: {signal} (ثقة: {confidence}%)")
            
            return analysis
            
        except Exception as e:
            logger.error(f"خطأ في تحليل {symbol}: {e}")
            return {"error": f"خطأ في التحليل: {str(e)}"}
    
    def _calculate_rsi(self, prices, period=14):
        """حساب RSI يدوياً"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_support_resistance(self, data, window=20):
        """حساب مستويات الدعم والمقاومة"""
        if len(data) < window:
            return data['Low'].min(), data['High'].max()
        
        support = data['Low'].rolling(window).min().iloc[-1]
        resistance = data['High'].rolling(window).max().iloc[-1]
        return support, resistance
    
    def _determine_trend(self, data, ma20, ma50, ma200):
        """تحديد الاتجاه وقوته"""
        price = data['Close'].iloc[-1]
        
        # اتجاه قصير المدى
        short_trend = "صاعد" if price > ma20 else "هابط"
        
        # اتجاه طويل المدى
        long_trend = "صاعد" if ma20 > ma50 > ma200 else "هابط" if ma20 < ma50 < ma200 else "جانبي"
        
        # قوة الاتجاه
        strength = 0
        if short_trend == long_trend:
            strength = 85  # قوي
        elif long_trend == "جانبي":
            strength = 50  # متوسط
        else:
            strength = 30  # ضعيف
        
        trend = f"{short_trend} ({long_trend})"
        return trend, strength
    
    def _generate_signal(self, data, price, ma20, ma50, rsi, support, resistance):
        """توليد إشارة تداول"""
        # تحليل متعدد الأبعاد
        signals = []
        confidences = []
        
        # إشارة المتوسطات المتحركة
        if price > ma20 > ma50:
            signals.append("شراء")
            confidences.append(70)
        elif price < ma20 < ma50:
            signals.append("بيع")
            confidences.append(70)
        else:
            signals.append("حياد")
            confidences.append(40)
        
        # إشارة RSI
        if rsi < 30:
            signals.append("شراء")
            confidences.append(75)
        elif rsi > 70:
            signals.append("بيع")
            confidences.append(75)
        else:
            signals.append("حياد")
            confidences.append(50)
        
        # إشارة الدعم والمقاومة
        distance_to_support = abs(price - support) / price
        distance_to_resistance = abs(price - resistance) / price
        
        if distance_to_support < 0.01:  # قريب من الدعم
            signals.append("شراء")
            confidences.append(80)
        elif distance_to_resistance < 0.01:  # قريب من المقاومة
            signals.append("بيع")
            confidences.append(80)
        
        # اتخاذ القرار النهائي
        buy_signals = signals.count("شراء")
        sell_signals = signals.count("بيع")
        
        if buy_signals > sell_signals:
            final_signal = "شراء"
            confidence = np.mean([c for s, c in zip(signals, confidences) if s == "شراء"])
        elif sell_signals > buy_signals:
            final_signal = "بيع"
            confidence = np.mean([c for s, c in zip(signals, confidences) if s == "بيع"])
        else:
            final_signal = "انتظار"
            confidence = np.mean(confidences)
        
        return final_signal, min(95, confidence)
    
    def get_detailed_analysis(self, symbol: str) -> str:
        """تحليل فني مفصل مع توصيات"""
        analysis = self.analyze_symbol(symbol)
        
        if 'error' in analysis:
            return f"❌ {analysis['error']}"
        
        # رموز تعبيرية حسب الإشارة
        emoji = "🟢" if analysis['signal'] == 'شراء' else "🔴" if analysis['signal'] == 'بيع' else "🟡"
        trend_emoji = "📈" if "صاعد" in analysis['trend'] else "📉" if "هابط" in analysis['trend'] else "↔️"
        
        return f"""
{emoji} **تحليل مفصل لـ {symbol}**

💰 **السعر الحالي:** {analysis['current_price']:.4f}
{trend_emoji} **الاتجاه:** {analysis['trend']}
⚡ **قوة الاتجاه:** {analysis['trend_strength']}%
🎯 **الإشارة:** {analysis['signal']}
📊 **الثقة:** {analysis['confidence']:.0f}%

📈 **المؤشرات الفنية:**
• RSI: {analysis['rsi']:.1f} {'(مشترى زائد)' if analysis['rsi'] < 30 else '(مبيع زائد)' if analysis['rsi'] > 70 else '(محايد)'}
• المتوسط 20: {analysis['ma20']:.4f}
• المتوسط 50: {analysis['ma50']:.4f}
• المتوسط 200: {analysis['ma200']:.4f}
• التقلب السنوي: {analysis['volatility']:.2%}

🎯 **المستويات الرئيسية:**
• الدعم: {analysis['support']:.4f}
• المقاومة: {analysis['resistance']:.4f}

💡 **التوصيات:**
{self._get_trading_recommendations(analysis)}
        """
    
    def _get_trading_recommendations(self, analysis):
        """توصيات تداول مخصصة"""
        recommendations = []
        
        if analysis['signal'] == 'شراء' and analysis['confidence'] > 70:
            recommendations.append("• 🟢 فرصة شراء قوية")
            recommendations.append(f"• 🎯 الدخول حول: {analysis['current_price']:.4f}")
            recommendations.append(f"• 🛑 وقف الخسارة: {analysis['support']:.4f}")
            recommendations.append(f"• 🎯 الهدف: {analysis['resistance']:.4f}")
        elif analysis['signal'] == 'بيع' and analysis['confidence'] > 70:
            recommendations.append("• 🔴 فرصة بيع قوية")
            recommendations.append(f"• 🎯 الدخول حول: {analysis['current_price']:.4f}")
            recommendations.append(f"• 🛑 وقف الخسارة: {analysis['resistance']:.4f}")
            recommendations.append(f"• 🎯 الهدف: {analysis['support']:.4f}")
        else:
            recommendations.append("• 🟡 انتظر إشارة أوضح")
            recommendations.append("• 📊 راقب突破 المستويات")
            recommendations.append("• ⚠️ تجنب التداول الآن")
        
        return "\n".join(recommendations)
    
    def get_market_analysis(self) -> str:
        """تحليل السوق العام"""
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'USOIL']
        analysis_text = "📈 **تحليل السوق الشامل:**\n\n"
        
        for symbol in symbols:
            try:
                analysis = self.analyze_symbol(symbol)
                if 'error' not in analysis:
                    emoji = "🟢" if analysis['signal'] == 'شراء' else "🔴" if analysis['signal'] == 'بيع' else "🟡"
                    analysis_text += f"{emoji} **{symbol}**: {analysis['signal']} (ثقة: {analysis['confidence']:.0f}%)\n"
                    analysis_text += f"   السعر: {analysis['current_price']:.4f} | RSI: {analysis['rsi']:.1f}\n\n"
            except Exception as e:
                analysis_text += f"❌ {symbol}: غير متوفر\n\n"
        
        # إضافة توصيات عامة
        analysis_text += "\n💡 **التوصيات الاستراتيجية:**\n"
        analysis_text += "• 🎯 ركز على الأزواج ذات الإشارات القوية (>70% ثقة)\n"
        analysis_text += "• ⏰ تداول خلال الجلسات النشطة\n"
        analysis_text += "• 🛑 استخدم أوامر وقف الخسارة دائماً\n"
        analysis_text += "• 📊 تنويع المحفظة لتقليل المخاطر\n"
        analysis_text += "• 📈 اتبع إدارة المخاطرة (2-3% لكل صفقة)"
        
        return analysis_text
    
    def get_trading_signals(self) -> Dict[str, Dict]:
        """إشارات التداول لجميع الرموز"""
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'XAUUSD', 'USOIL']
        signals = {}
        
        for symbol in symbols:
            try:
                analysis = self.analyze_symbol(symbol)
                if 'error' not in analysis:
                    signals[symbol] = {
                        'signal': analysis['signal'],
                        'confidence': analysis['confidence'],
                        'current_price': analysis['current_price'],
                        'rsi': analysis['rsi'],
                        'trend': analysis['trend'],
                        'timestamp': analysis['timestamp']
                    }
            except Exception as e:
                logger.error(f"خطأ في إشارة {symbol}: {e}")
        
        # ترتيب الإشارات حسب الثقة
        sorted_signals = dict(sorted(signals.items(), 
                                   key=lambda x: x[1]['confidence'], 
                                   reverse=True))
        
        return sorted_signals
    
    def get_signal_history(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """الحصول على سجل الإشارات"""
        if symbol:
            history = [s for s in self.signals_history if s['symbol'] == symbol]
        else:
            history = self.signals_history
        
        return history[-limit:] if history else []