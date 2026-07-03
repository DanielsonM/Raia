from flask import Flask, request
import requests
from telegram.ext import Updater, CommandHandler

app = Flask(__name__)

TELEGRAM_TOKEN = "8865758481:AAGLIM9Fwd04ebzW1ra6TvkXI4g1swi8bwY"
GROUP_ID = -123456789  # Substitua pelo ID real do seu grupo privado
LINK_PAGAMENTO = "https://link.mercadopago.com.br/raiabot"

# --- BOT TELEGRAM ---
def start(update, context):
    update.message.reply_text("Olá! Bem-vindo ao meu bot de cursos.\nDigite /comprar para acessar o link de pagamento.")

def comprar(update, context):
    update.message.reply_text(f"Para adquirir o curso, clique aqui: {LINK_PAGAMENTO}")

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("comprar", comprar))

# --- WEBHOOK MERCADO PAGO ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    # Verifique o evento recebido
    if data.get("action") == "payment.created":
        payment_status = data["data"]["status"]
        # Aqui você precisa garantir que o 'telegram_id' do aluno esteja nos metadados do pagamento
        user_id = data["data"]["metadata"].get("telegram_id")

        if payment_status == "approved" and user_id:
            # Adiciona o usuário ao grupo privado
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/inviteChatMember"
            payload = {"chat_id": GROUP_ID, "user_id": user_id}
            requests.post(url, data=payload)
    return "ok"

if __name__ == "__main__":
    # O bot roda em paralelo ao servidor Flask
    updater.start_polling()
    app.run(port=5000)
