import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- VARIÁVEIS DE AMBIENTE ---
MERCADO_PAGO_TOKEN = os.environ["MERCADO_PAGO_TOKEN"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
LINK_PAGAMENTO = os.environ["LINK_PAGAMENTO"]

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# --- ROTA ÚNICA PARA O WEBHOOK DO TELEGRAM ---
@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    data = request.json
    
    # Verifica se a mensagem existe no payload
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text_received = data["message"]["text"].strip()

        # Condicional para ler o comando digitado pelo usuário
        if text_received == "/start":
            send_message(chat_id, "Olá! Bem-vindo.\nDigite /comprar para acessar o link de pagamento.")
        
        elif text_received == "/comprar":
            send_message(chat_id, f"Para adquirir o curso, clique aqui: {LINK_PAGAMENTO}")
            
    return "ok"

# --- WEBHOOK MERCADO PAGO ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("action") == "payment.created":
        payment_info = data.get("data", {})
        payment_status = payment_info.get("status")
        metadata = payment_info.get("metadata", {})
        user_id = metadata.get("telegram_id")

        if payment_status == "approved" and user_id:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/createChatInviteLink"
            payload = {"chat_id": GROUP_ID}
            response = requests.post(url, json=payload)
            invite_link = response.json()["result"]["invite_link"]

            send_message(user_id, f"✅ Pagamento aprovado!\nAcesse o grupo do curso aqui: {invite_link}")

    return "ok"

# --- ROTA DE SAÚDE ---
@app.route("/healthz")
def healthz():
    return "ok"