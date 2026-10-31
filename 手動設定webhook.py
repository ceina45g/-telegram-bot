import requests

# 1. 你的 Bot Token (正確)
TOKEN = "7844559948:AAED2hkAOcLc2CqG_malaH3DqUMhpa5JWu0"

# 2. 已自動填入 ngrok 產生的網址
WEBHOOK_URL = "https://9df8-219-71-33-17.ngrok-free.app/webhook"

print(f"嘗試將 Webhook 設定為: {WEBHOOK_URL}")

# 執行設定
url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
resp = requests.get(url)

print("設定結果：")
print(resp.json())
