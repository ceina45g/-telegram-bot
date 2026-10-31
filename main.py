import os
import time
import threading
import requests
from dotenv import load_dotenv
import telebot

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取 Bot Token 與 Chat ID
BOT_TOKEN = os.environ.get('BOT_TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN', "8912918375:AAG-Iv674UC8N5PCJzwGrpYkMFvh4JutTbk")
CHAT_ID = os.environ.get('CHAT_ID') or os.environ.get('TELEGRAM_CHAT_ID', "1418292007")
MINER_WALLET = os.environ.get('MINER_WALLET', "13NvdBs5dFarwR4TK373BMM4sEheAXbewB")
POOL_API_URL = f"https://pool.nerdminers.org/users/{MINER_WALLET}"

bot = telebot.TeleBot(BOT_TOKEN)

# 狀態追蹤
monitor_state = {
    "last_workers": None,
    "last_best_share": 0.0,
    "initialized": False
}

def fetch_mining_stats():
    try:
        resp = requests.get(POOL_API_URL, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Fetch stats error: {e}")
    return None

def background_monitor():
    """背景執行緒：定時檢查算力與礦工狀態，並發送主動通知"""
    print("🚀 語娃娃背景監控執行緒已啟動...")
    while True:
        try:
            stats = fetch_mining_stats()
            if stats:
                workers = stats.get('workers', 0)
                best_share = stats.get('bestshare', 0.0)
                hashrate_1h = stats.get('hashrate1hr', '0')

                if not monitor_state["initialized"]:
                    monitor_state["last_workers"] = workers
                    monitor_state["last_best_share"] = best_share
                    monitor_state["initialized"] = True
                    print(f"📊 初始狀態載入: workers={workers}, best_share={best_share}")
                else:
                    # 1. 檢查線上工人狀態變更 (上下線通知)
                    if workers != monitor_state["last_workers"]:
                        if workers > monitor_state["last_workers"]:
                            msg = f"🟢 **【語娃娃礦機上線通知】**\n偵測到礦工上線！目前線上工人數：`{workers}` (算力: {hashrate_1h})"
                        else:
                            msg = f"🔴 **【語娃娃礦機離線警報】**\n注意！線上工人數減少：`{workers}`"
                        try:
                            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                        except Exception as e:
                            print(f"Send worker alert error: {e}")
                        monitor_state["last_workers"] = workers

                    # 2. 檢查爆礦 / 專家 Share 刷新 (爆礦通知)
                    if best_share > monitor_state["last_best_share"]:
                        diff = best_share - monitor_state["last_best_share"]
                        msg = (
                            f"🎉 **【語娃娃·爆礦/高難度 Share 捷報！】**\n"
                            "━━━━━━━━━━━━━━━━━━━\n"
                            f"🏆 最佳 Share 刷新！\n"
                            f"舊紀錄：`{monitor_state['last_best_share']:.2f}`\n"
                            f"新紀錄：`{best_share:.2f}` (+`{diff:.2f}`)\n"
                            f"⚡ 目前算力 (1h)：`{hashrate_1h}`\n"
                            "━━━━━━━━━━━━━━━━━━━"
                        )
                        try:
                            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                        except Exception as e:
                            print(f"Send best share alert error: {e}")
                        monitor_state["last_best_share"] = best_share

        except Exception as e:
            print(f"Background monitor loop error: {e}")

        time.sleep(60)  # 每 60 秒檢查一次

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 你好！我是 **語娃娃** 礦機監控機器人\n\n"
        "📍 礦池：`pool.nerdminer.io:3333` (官方備用池)\n"
        f"👛 錢包：`{MINER_WALLET}`\n\n"
        "🛠️ 可用指令：\n"
        "/status 或 /stats - 查詢即時挖礦算力與礦工狀態\n"
        "/help - 顯示此說明選單\n\n"
        "✨ **功能特色**：已啟動背景自動監控與爆礦/上下線主動推播通知！"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['status', 'stats'])
def send_mining_status(message):
    stats = fetch_mining_stats()
    if not stats:
        bot.reply_to(message, "⚠️ 無法連線至礦池 API 或尚未有挖礦數據記錄。")
        return

    hashrate_1h = stats.get('hashrate1hr', '0')
    hashrate_1d = stats.get('hashrate1d', '0')
    hashrate_7d = stats.get('hashrate7d', '0')
    workers = stats.get('workers', 0)
    best_share = stats.get('bestshare', 0.0)
    shares = stats.get('shares', 0.0)

    report = (
        "📊 **語娃娃 - 礦機即時監控報告**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📍 礦池：`pool.nerdminer.io:3333`\n"
        f"👛 錢包：`{MINER_WALLET[:6]}...{MINER_WALLET[-6:]}`\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ 1小時算力：`{hashrate_1h}`\n"
        f"⚡ 1天算力：`{hashrate_1d}`\n"
        f"⚡ 7天算力：`{hashrate_7d}`\n"
        f"👷 線上工人數：`{workers}`\n"
        f"🏆 最佳 Share：`{best_share:.2f}`\n"
        f"📦 總 Shares：`{shares}`\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 背景監控中（每 60 秒自動檢查爆礦與上下線）"
    )
    bot.reply_to(message, report, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, f"🤖 語娃娃收到您的訊息：{message.text}\n💡 請輸入 /status 查詢礦機算力狀態。")

if __name__ == "__main__":
    print("語娃娃 Telegram Bot 開始運行...")
    # 啟動背景監控執行緒
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()

    # 啟動 Telegram 輪詢
    bot.infinity_polling()
