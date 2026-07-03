from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
LINK_PAGAMENTO = os.environ["LINK_PAGAMENTO"]

# --- FUNÇÕES DO BOT ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)

@app.route("/start", methods=["POST"])
def start():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    send_message(chat_id, "Olá! Bem-vindo ao meu bot de cursos.\nDigite /comprar para acessar o link de pagamento.")
    return "ok"

@app.route("/comprar", methods=["POST"])
def comprar():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    send_message(chat_id, f"Para adquirir o curso, clique aqui: {LINK_PAGAMENTO}")
    return "ok"

# --- WEBHOOK MERCADO PAGO ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("action") == "payment.created":
        payment_status = data["data"]["status"]
        user_id = data["data"]["metadata"].get("telegram_id")

        if payment_status == "approved" and user_id:
            # Cria link de convite para o grupo
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/createChatInviteLink"
            payload = {"chat_id": GROUP_ID}
            response = requests.post(url, data=payload)
            invite_link = response.json()["result"]["invite_link"]

            # Envia o link para o usuário
            send_message(user_id, f"✅ Pagamento aprovado!\nAcesse o grupo do curso aqui: {invite_link}")
    return "ok"

# --- ROTA DE SAÚDE (Render usa para checar se está ativo) ---
@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
