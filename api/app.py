from flask import Flask, request
import telebot

app = Flask(__name__)

@app.route('/bot', methods=['GET'])
def activate_bot():
    token = request.args.get('token')
    if not token:
        return "Token do bot não fornecido.", 400

    # Iniciar o bot com o token fornecido
    bot = telebot.TeleBot(token)

    # Define o comando start
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Bot ativado e comando /start recebido!")

    # Inicia o bot em modo polling
    try:
        bot.polling()
        return "Bot ativado com sucesso.", 200
    except Exception as e:
        return f"Erro ao ativar o bot: {e}", 500

if __name__ == '__main__':
    app.run(port=5000)
