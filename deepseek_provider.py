import requests
import os
import logging
import json
from typing import Dict, Optional
from config import CONFIG

logger = logging.getLogger(__name__)

class DeepSeekProvider:
    """مزود DeepSeek AI المحسن مع معالجة أخطاء شاملة"""
    
    def __init__(self):
        self.api_key = CONFIG.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        self.timeout = 30
        self.max_retries = 3
        self._session = requests.Session()
        
    def is_configured(self) -> bool:
        """التحقق من إعدادات API"""
        return bool(self.api_key and self.api_key != 'your_deepseek_api_key_here')
    
    def analyze_market(self, symbol: str, market_data: Dict) -> Dict:
        """
        تحليل السوق باستخدام DeepSeek AI مع معالجة أخطاء متقدمة
        
        Args:
            symbol: زوج العملة
            market_data: بيانات السوق
            
        Returns:
            dict: نتائج التحليل
        """
        if not self.is_configured():
            logger.warning("DeepSeek غير مضبوط - استخدام التحليل المحاكى")
            return self.get_simulated_analysis(symbol, market_data)
        
        for attempt in range(self.max_retries):
            try:
                prompt = self._build_analysis_prompt(symbol, market_data)
                response = self._send_analysis_request(prompt)
                
                if response['success']:
                    analysis_result = self._parse_analysis_result(response['data'], symbol, market_data)
                    logger.info(f"تحليل DeepSeek ناجح لـ {symbol} (محاولة {attempt + 1})")
                    return analysis_result
                else:
                    logger.warning(f"محاولة {attempt + 1} فشلت: {response.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"خطأ في المحاولة {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("جميع محاولات DeepSeek فشلت - استخدام المحاكاة")
                    return self.get_simulated_analysis(symbol, market_data)
        
        return self.get_simulated_analysis(symbol, market_data)
    
    def _send_analysis_request(self, prompt: str) -> Dict:
        """إرسال طلب التحليل إلى API"""
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500,
                "top_p": 0.9
            }
            
            response = self._session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.Timeout:
            error_msg = "انتهت المهلة أثناء الاتصال بـ DeepSeek"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "خطأ في الاتصال بـ DeepSeek"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"خطأ HTTP من DeepSeek: {e.response.status_code}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"خطأ غير متوقع في DeepSeek: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def _get_system_prompt(self) -> str:
        """الحصول على prompt النظام"""
        return """أنت محلل فني محترف في أسواق العملات والأسهم. 
قم بتحليل البيانات المقدمة وأعط تحليلاً شاملاً يتضمن:

1. تحليل الاتجاه العام
2. تحليل الزخم والمؤشرات الفنية  
3. مستويات الدعم والمقاومة الرئيسية
4. توصية تداول واضحة (شراء/بيع/انتظار)
5. إدارة المخاطرة والمستويات المقترحة

كن دقيقاً وواقعياً في تحليلك. استخدم مصطلحات فنية مناسبة."""

    def _build_analysis_prompt(self, symbol: str, market_data: Dict) -> str:
        """بناء prompt تحليلي محترف"""
        
        # استخراج البيانات الأساسية
        current_price = market_data.get('close', 'غير معروف')
        high = market_data.get('high', 'غير معروف')
        low = market_data.get('low', 'غير معروف')
        timeframe = market_data.get('timeframe', 'غير محدد')
        
        # البيانات المتقدمة إذا كانت متوفرة
        advanced_analysis = market_data.get('advanced_analysis', {})
        technical = advanced_analysis.get('technical_analysis', {})
        fundamental = advanced_analysis.get('fundamental_analysis', {})
        
        prompt = f"""
🔍 طلب تحليل فني متقدم للزوج: {symbol}

📊 البيانات الأساسية:
- السعر الحالي: {current_price}
- أعلى سعر: {high}
- أدنى سعر: {low}  
- الإطار الزمني: {timeframe}

📈 البيانات الفنية:
"""
        
        if technical and 'error' not in technical:
            indicators = technical.get('indicators', {})
            trend = technical.get('trend', {})
            momentum = technical.get('momentum', {})
            
            prompt += f"""
- المتوسطات المتحركة:
  • MA20: {indicators.get('moving_averages', {}).get('ma_20', 'N/A')}
  • MA50: {indicators.get('moving_averages', {}).get('ma_50', 'N/A')}
  • MA200: {indicators.get('moving_averages', {}).get('ma_200', 'N/A')}

- مؤشرات الزخم:
  • RSI: {momentum.get('rsi', 'N/A')} ({momentum.get('rsi_signal', 'N/A')})
  • MACD: {momentum.get('macd', 'N/A')} ({momentum.get('macd_signal', 'N/A')})

- الاتجاه: {trend.get('direction', 'N/A')} - القوة: {trend.get('strength', 'N/A')}
"""
        
        if fundamental and 'error' not in fundamental:
            news_analysis = fundamental.get('news_analysis', {})
            interest_analysis = fundamental.get('interest_analysis', {})
            
            prompt += f"""
📰 البيانات الأساسية:
- توصية الأخبار: {news_analysis.get('recommendation', 'N/A')}
- تأثير الفائدة: {interest_analysis.get('effect', 'N/A')}
- فارق الفائدة: {interest_analysis.get('differential', 'N/A')}%
"""
        
        prompt += """

🎯 المطلوب:
1. تحليل فني شامل للزوج
2. تقييم الاتجاه والزخم الحالي
3. تحديد مستويات الدعم والمقاومة الرئيسية
4. توصية تداول واضحة مع المبررات
5. اقتراحات إدارة المخاطرة

يرجى تقديم إجابة منظمة وواقعية وقابلة للتطبيق."""

        return prompt

    def _parse_analysis_result(self, api_response: Dict, symbol: str, market_data: Dict) -> Dict:
        """تحليل استجابة API واستخراج المعلومات المهمة"""
        try:
            if 'choices' not in api_response or not api_response['choices']:
                raise ValueError("لا توجد خيارات في الاستجابة")
            
            message_content = api_response['choices'][0]['message']['content']
            
            # استخراج التوصية من النص
            recommendation = self._extract_recommendation(message_content)
            
            # تحليل الثقة بناءاً على طول ووضوح الرد
            confidence = self._calculate_confidence(message_content)
            
            return {
                'success': True,
                'symbol': symbol,
                'recommendation': recommendation,
                'analysis': message_content,
                'confidence': confidence,
                'provider': 'DeepSeek AI',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل استجابة DeepSeek: {str(e)}")
            return self.get_simulated_analysis(symbol, market_data)

    def _extract_recommendation(self, analysis_text: str) -> str:
        """استخراج التوصية من نص التحليل"""
        analysis_lower = analysis_text.lower()
        
        if any(word in analysis_lower for word in ['شراء', 'بيع', 'شرائى', 'بيعى', 'buy', 'sell']):
            if 'شراء' in analysis_lower or 'buy' in analysis_lower:
                return 'شراء'
            elif 'بيع' in analysis_lower or 'sell' in analysis_lower:
                return 'بيع'
        
        return 'انتظار'

    def _calculate_confidence(self, analysis_text: str) -> float:
        """حساب ثقة التحليل بناءاً على جودة النص"""
        # تحليل طول النص
        text_length = len(analysis_text)
        length_score = min(text_length / 500, 1.0)  # 500 حرف كحد مثالي
        
        # تحليل التنظيم (عدد الأسطر)
        lines = analysis_text.split('\n')
        structure_score = min(len(lines) / 10, 1.0)  # 10 أسطر كحد مثالي
        
        # تحليل وجود كلمات رئيسية
        key_terms = ['دعم', 'مقاومة', 'اتجاه', 'زخم', 'هدف', 'وقف', 'مخاطرة']
        term_count = sum(1 for term in key_terms if term in analysis_text)
        terms_score = min(term_count / len(key_terms), 1.0)
        
        confidence = (length_score + structure_score + terms_score) / 3
        return round(confidence, 2)

    def get_simulated_analysis(self, symbol: str, market_data: Dict) -> Dict:
        """تحليل محاكى للاختبار بدون API"""
        try:
            current_price = market_data.get('close', 1.0)
            advanced_analysis = market_data.get('advanced_analysis', {})
            technical = advanced_analysis.get('technical_analysis', {})
            
            # تحليل مبني على البيانات الفنية
            if technical and 'error' not in technical:
                trend = technical.get('trend', {})
                momentum = technical.get('momentum', {})
                
                if trend.get('direction') == 'bullish' and momentum.get('rsi_signal') != 'overbought':
                    recommendation = 'شراء'
                    reasoning = "الاتجاه صاعد والزخم إيجابي"
                elif trend.get('direction') == 'bearish' and momentum.get('rsi_signal') != 'oversold':
                    recommendation = 'بيع'
                    reasoning = "الاتجاه هابط والزخم سلبي"
                else:
                    recommendation = 'انتظار'
                    reasoning = "السوق في حالة اتزان أو انتظار"
            else:
                # تحليل مبني على السعر فقط
                if current_price > 1.08:
                    recommendation = 'بيع'
                    reasoning = "السعر عند مستويات مرتفعة"
                elif current_price < 1.07:
                    recommendation = 'شراء' 
                    reasoning = "السعر عند مستويات منخفضة"
                else:
                    recommendation = 'انتظار'
                    reasoning = "السوق في نطاق جانبي"
            
            analysis_text = f"""
📊 تحليل محاكى لـ {symbol}

💰 السعر الحالي: {current_price}
🎯 التوصية: {recommendation}

🔍 التحليل:
{reasoning}

📈 ملاحظات:
- هذا تحليل محاكى للاختبار
- يوصى باستخدام DeepSeek الحقيقي لدقة أفضل
- المراجعة المستمرة لإدارة المخاطرة

⚡ إدارة المخاطرة المقترحة:
- وقف الخسارة: {current_price * 0.98:.4f}
- الهدف الأول: {current_price * 1.02:.4f}
- نسبة العائد للمخاطرة: 1:2
"""
            
            return {
                'success': True,
                'symbol': symbol,
                'recommendation': recommendation,
                'analysis': analysis_text,
                'confidence': 0.7,
                'provider': 'المحاكاة للاختبار',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"خطأ في التحليل المحاكى: {str(e)}")
            return {
                'success': False,
                'symbol': symbol,
                'recommendation': 'انتظار',
                'analysis': 'فشل في التحليل',
                'confidence': 0.0,
                'provider': 'المحاكاة',
                'error': str(e)
            }

    def _get_current_timestamp(self) -> str:
        """الحصول على الطابع الزمني الحالي"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def test_connection(self) -> Dict:
        """اختبار اتصال DeepSeek"""
        if not self.is_configured():
            return {'success': False, 'error': 'API key not configured'}
        
        try:
            test_prompt = "اختبار اتصال. الرجاء الرد بـ 'OK' فقط."
            response = self._send_analysis_request(test_prompt)
            
            if response['success']:
                return {'success': True, 'message': 'الاتصال بنجاح'}
            else:
                return {'success': False, 'error': response.get('error', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


# اختبار الوحدة
if __name__ == "__main__":
    def test_deepseek_provider():
        """اختبار مزود DeepSeek"""
        provider = DeepSeekProvider()
        
        print("🔍 اختبار DeepSeek Provider...")
        
        # اختبار التكوين
        if not provider.is_configured():
            print("⚠️ DeepSeek غير مضبوط - اختبار المحاكاة")
        
        # بيانات اختبارية
        test_data = {
            'close': 1.0850,
            'high': 1.0870,
            'low': 1.0820,
            'timeframe': 'H1',
            'advanced_analysis': {
                'technical_analysis': {
                    'trend': {'direction': 'bullish', 'strength': 'strong'},
                    'momentum': {'rsi': 58.5, 'rsi_signal': 'neutral'}
                }
            }
        }
        
        result = provider.analyze_market('EURUSD', test_data)
        
        if result['success']:
            print(f"✅ التحليل ناجح: {result['recommendation']}")
            print(f"📊 الثقة: {result['confidence']}")
            print(f"🤖 المزود: {result['provider']}")
        else:
            print(f"❌ فشل التحليل: {result.get('error', 'Unknown error')}")
        
        print("✅ اختبار DeepSeek Provider مكتمل")
    
    test_deepseek_provider()