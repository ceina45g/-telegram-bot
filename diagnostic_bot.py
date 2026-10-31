import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7844559948:AAED2hkAOcLc2CqG_malaH3DqUMhpa5JWu0"
USER_CHAT_ID = "1418292007"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"收到 /start 指令，來自: {update.effective_chat.id}")
    await update.message.reply_text(f"👋 診斷機器人已收到你的指令！目前時間: {datetime.now().strftime('%H:%M:%S')}")

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text if update.message else "None"
    logger.info(f"--- 偵測到訊息 ---")
    logger.info(f"來自: {user.first_name} (ID: {user.id})")
    logger.info(f"內容: {text}")
    await update.message.reply_text(f"我收到了你的訊息：{text}")

async def send_startup_msg(application: Application):
    logger.info(f"嘗試發送啟動測試訊息給 {USER_CHAT_ID}...")
    try:
        await application.bot.send_message(chat_id=USER_CHAT_ID, text=f"🚀 診斷機器人已在背景啟動！請傳送 /start 或隨意傳送訊息測試回應。")
        logger.info("啟動訊息發送成功。")
    except Exception as e:
        logger.error(f"啟動訊息發送失敗: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, monitor))
    
    # 在啟動時發送訊息
    loop = asyncio.get_event_loop()
    loop.create_task(send_startup_msg(application))

    logger.info("機器人開始執行...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
