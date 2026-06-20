import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد تسجيل الأخطاء والبيانات (Logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# جلب توكن البوت من متغيرات البيئة في Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# دالة الترحيب عند كتابة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت تحميل الفيديوهات! 🎬\n\n"
        "أرسل لي رابط الفيديو من (TikTok, Instagram, YouTube...) وسأقوم بجلبه لك فوراً."
    )

# دالة معالجة الروابط وتحميل الفيديو
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_sent = update.message.text.strip()
    
    # التحقق من أن النص المرسل هو رابط فعلي
    if not url_sent.startswith(("http://", "https://")):
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    await update.message.reply_text("⏳ جاري استخراج الفيديو... انتظر لحظة.")

    try:
        # استخدام واجهة Cobalt لاستخراج الفيديو
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url_sent,
            "videoQuality": "720", 
            "audioFormat": "mp3"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # التحقق من نجاح العملية والحصول على الرابط المباشر
            if data.get("status") in ["stream", "picker"]:
                video_url = data.get("url")
                
                # إرسال الفيديو للمستخدم داخل التليجرام
                await context.bot.send_video(
                    chat_id=update.message.chat_id,
                    video=video_url,
                    caption="✨ تم التحميل بنجاح!"
                )
            else:
                await update.message.reply_text("❌ عذراً، لم أتمكن من استخراج هذا الفيديو. قد يكون الحساب خاصاً أو الرابط غير مدعوم.")
        else:
            await update.message.reply_text("❌ حدث خطأ أثناء الاتصال بخدمة التحميل، يرجى المحاولة لاحقاً.")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await update.message.reply_text("❌ عذراً، حدث خطأ غير متوقع أثناء معالجة الرابط.")

# الدالة الرئيسية لتشغيل البوت
def main():
    if not TELEGRAM_TOKEN:
        logging.error("TELEGRAM_TOKEN is missing! Please set it in Render environment variables.")
        return

    # بناء التطبيق باستخدام التوكن الصحيح (التحديث الجديد للمكتبة)
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # ربط الأوامر والرسائل بالدوال الخاصة بها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # بدء تشغيل البوت واستقبال الرسائل بشكل مستمر
    application.run_polling()

if __name__ == '__main__':
    main()
    
