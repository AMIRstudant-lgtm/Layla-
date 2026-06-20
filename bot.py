import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تفعيل تسجيل الأخطاء لرؤيتها في لوحة تحكم Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# جلب توكن البوت من بيئة العمل لحمايته
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت تحميل الفيديوهات! 🎬\n\n"
        "كل ما عليك فعله هو إرسال رابط الفيديو من (TikTok, Instagram, YouTube...) وسأقوم بجلبه لك فوراً."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_sent = update.message.text.strip()
    
    # التأكد من أن المستخدم أرسل رابطاً فعلياً وليس كلاماً عادياً
    if not url_sent.startswith(("http://", "https://")):
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    await update.message.reply_text("⏳ جاري استخراج الفيديو... انتظر لحظة.")

    try:
        # استخدام API مجاني وقوي لاستخراج الروابط المباشرة (مثل خدمة Cobalt الشهيرة أو خدمات مشابهة)
        # هذا الـ API يعالج الرابط ويعطينا رابط الفيديو المباشر
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url_sent,
            "videoQuality": "720", # جودة متوسطة ومناسبة للتليجرام
            "audioFormat": "mp3"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # إذا نجح الـ API في جلب الرابط المباشر
            if data.get("status") == "stream" or data.get("status") == "picker":
                video_url = data.get("url")
                
                # إرسال الفيديو للمستخدم مباشرة عبر الرابط دون تحميله على سيرفرنا
                await context.bot.send_video(
                    chat_id=update.message.chat_id,
                    video=video_url,
                    caption="✨ تم التحميل بنجاح بواسطة بوتك!"
                )
            else:
                await update.message.reply_text("❌ عذراً، لم أتمكن من استخراج هذا الفيديو. قد يكون الحساب خاصاً أو الرابط غير مدعوم.")
        else:
            await update.message.reply_text("❌ حدث خطأ أثناء الاتصال بخدمة التحميل، يرجى المحاولة لاحقاً.")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await update.message.reply_text("❌ عذراً، حدث خطأ غير متوقع أثناء معالجة الرابط.")

def main():
    # بناء وتوصيل البوت
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # الموجهات (Handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تشغيل البوت بنظام Polling المستمر
    application.run_polling()

if __name__ == '__main__':
    main()
