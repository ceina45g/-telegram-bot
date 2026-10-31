import requests

TOKEN = "7844559948:AAED2hkAOcLc2CqG_malaH3DqUMhpa5JWu0"

resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print("Webhook 狀態資訊：")
print(resp.json())
