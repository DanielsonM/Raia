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
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text_received = data["message"]["text"].strip()

        if text_received == "/start":
            send_message(chat_id, "Olá! Bem-vindo.\nDigite /comprar para acessar o link de pagamento.")
        elif text_received == "/comprar":
            send_message(chat_id, f"Para adquirir o curso, clique aqui: {LINK_PAGAMENTO}")
            
    return "ok"


# =====================================================================
#  COLE O NOVO CÓDIGO EXATAMENTE AQUI (SUBSTITUINDO O WEBHOOK ANTIGO)
# =====================================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("action") == "payment.created" or data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id") or data.get("id")
        
        if payment_id:
            url_mp = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {
                "Authorization": f"Bearer {MERCADO_PAGO_TOKEN}"
            }
            
            try:
                response_mp = requests.get(url_mp, headers=headers)
                
                if response_mp.status_code == 200:
                    payment_info = response_mp.json()
                    payment_status = payment_info.get("status")
                    metadata = payment_info.get("metadata", {})
                    user_id = metadata.get("telegram_id")

                    if payment_status == "approved" and user_id:
                        url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/createChatInviteLink"
                        payload_tg = {"chat_id": GROUP_ID}
                        response_tg = requests.post(url_tg, json=payload_tg)
                        
                        invite_link = response_tg.json()["result"]["invite_link"]
                        send_message(user_id, f"✅ Pagamento aprovado!\nAcesse o grupo do curso aqui: {invite_link}")
                else:
                    print(f"Erro ao consultar Mercado Pago: Status {response_mp.status_code}")
            
            except Exception as e:
                print(f"Erro de conexão com a API do Mercado Pago: {e}")

    return "ok", 200
# =====================================================================


# --- ROTA DE SAÚDE ---
@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    # Se você roda localmente ou em produção, a inicialização fica no final
    app.run(host="0.0.0.0", port=5000)