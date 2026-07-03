from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- VARIÁVEIS DE AMBIENTE ---
MERCADO_PAGO_TOKEN = os.environ["MERCADO_PAGO_TOKEN"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
LINK_PAGAMENTO = os.environ["LINK_PAGAMENTO"]

# --- FUNÇÕES DO BOT ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# --- ROTAS TELEGRAM ---
@app.route("/start", methods=["POST"])
def start():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    send_message(chat_id, "Olá! Bem-vindo.\nDigite /comprar para acessar o link de pagamento.")
    return "ok"

@app.route("/comprar", methods=["POST"])
def comprar():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    # Aqui você pode usar LINK_PAGAMENTO fixo ou gerar via API Mercado Pago
    send_message(chat_id, f"Para adquirir o curso, clique aqui: {LINK_PAGAMENTO}")
    return "ok"

# --- WEBHOOK MERCADO PAGO ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Verifica se é evento de pagamento
    if data.get("action") == "payment.created":
        payment_info = data.get("data", {})
        payment_status = payment_info.get("status")
        metadata = payment_info.get("metadata", {})
        user_id = metadata.get("telegram_id")

        if payment_status == "approved" and user_id:
            # Cria link de convite para o grupo
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/createChatInviteLink"
            payload = {"chat_id": GROUP_ID}
            response = requests.post(url, json=payload)
            invite_link = response.json()["result"]["invite_link"]

            # Envia o link para o usuário
            send_message(user_id, f"✅ Pagamento aprovado!\nAcesse o grupo do curso aqui: {invite_link}")

    return "ok"

# --- ROTA DE SAÚDE ---
@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
