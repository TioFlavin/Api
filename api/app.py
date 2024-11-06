import sqlite3
import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from mercadopago import SDK
from flask import Flask, request

# Configurações do bot
API_TOKEN = '7039287159:AAF1RkJJbXOkIXptr1SyCSx6wZ6J95BmonI'  # Substitua pelo seu token
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
db_path = 'loja.db'

# Inicializando o bot e Mercado Pago SDK
bot = telebot.TeleBot(API_TOKEN)
sdk = SDK('SEM TOKEN')  # Substitua pelo seu token do Mercado Pago

# Conexão com o banco de dados SQLite
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Criação da tabela de usuários
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY
    )
""")
conn.commit()

# Criação da tabela de projetos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        arquivo TEXT NOT NULL,
        file_id TEXT NOT NULL,  -- Armazenar file_id
        usuario_id INTEGER NOT NULL
    )
""")
conn.commit()

# Criação da tabela de tokens
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        usuario_id INTEGER PRIMARY KEY,
        token TEXT NOT NULL
    )
""")
conn.commit()

# Função para enviar o arquivo ao comprador
def send_file_to_user(file_id, chat_id):
    bot.send_document(chat_id, file_id)

# Função para verificar o token do dono
def check_token(usuario_id):
    cursor.execute("SELECT token FROM tokens WHERE usuario_id = ?", (usuario_id,))
    token = cursor.fetchone()
    return token

# Flask para criar o webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(data)])
    return '', 200

# Função para configurar o webhook
def set_webhook():
    webhook_url = os.getenv("VERCEL_URL") + '/webhook'  # Pega a URL do Vercel automaticamente
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

# Função para lidar com o comando /start
@bot.message_handler(commands=['start'])
def start(message):
    # Salvar o id do usuário no banco de dados
    cursor.execute("INSERT OR IGNORE INTO usuarios (id) VALUES (?)", (message.from_user.id,))
    conn.commit()

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Configuração (Token)", callback_data="config"))
    markup.add(InlineKeyboardButton("Produtos", callback_data="produtos"))
    markup.add(InlineKeyboardButton("Adicionar Produto", callback_data="adicionar_produto"))
    bot.send_message(message.chat.id, "Bem-vindo à loja! Selecione uma opção:", reply_markup=markup)

# Função para lidar com a opção "Configuração (Token)"
@bot.callback_query_handler(func=lambda call: call.data == 'config')
def config_token(call):
    bot.send_message(call.message.chat.id, "Digite seu token do Mercado Pago:")
    bot.register_next_step_handler(call.message, save_token)

# Função para salvar o token do Mercado Pago
def save_token(message):
    token = message.text.strip()
    cursor.execute("INSERT OR REPLACE INTO tokens (usuario_id, token) VALUES (?, ?)", (message.from_user.id, token))
    conn.commit()
    bot.send_message(message.chat.id, "Token do Mercado Pago salvo com sucesso!")

# Função para lidar com a opção "Adicionar Produto"
@bot.callback_query_handler(func=lambda call: call.data == "adicionar_produto")
def adicionar_produto(call):
    # Verifica se o usuário tem um token
    token = check_token(call.from_user.id)
    if not token:
        bot.send_message(call.message.chat.id, "Você precisa configurar o token do Mercado Pago primeiro. Digite o token agora:")
        bot.register_next_step_handler(call.message, save_token)
    else:
        bot.send_message(call.message.chat.id, "Por favor, envie o arquivo do produto (somente arquivos .zip).")
        bot.register_next_step_handler(call.message, process_project_file)

# Função para processar o arquivo do produto
@bot.message_handler(content_types=['document'])
def process_project_file(message):
    if message.document and message.document.file_name.endswith('.zip'):
        # Verifica o tamanho do arquivo
        if message.document.file_size > MAX_FILE_SIZE:
            bot.send_message(message.chat.id, "O arquivo é muito grande. O limite é 50 MB.")
            return

        file_info = bot.get_file(message.document.file_id)
        file_id = file_info.file_id  # Pega o ID do arquivo

        # Salva o arquivo no banco de dados (sem o preço por enquanto)
        cursor.execute("""
            INSERT INTO projetos (nome, preco, arquivo, file_id, usuario_id) 
            VALUES (?, ?, ?, ?, ?)
        """, (message.document.file_name.replace(".zip", ""), 0, "Caminho_arquivo", file_id, message.from_user.id))
        conn.commit()

        bot.send_message(message.chat.id, f"Arquivo '{message.document.file_name}' recebido. Agora, envie o valor do produto (exemplo: 10.50).")
        bot.register_next_step_handler(message, lambda msg: save_project(msg, file_id, message.document.file_name))  # Passando o nome do arquivo explicitamente

# Função para salvar o preço e concluir o processo do produto
def save_project(message, file_id, file_name):
    try:
        preco = float(message.text)
        # Atualiza o preço no banco de dados
        cursor.execute("""
            UPDATE projetos 
            SET preco = ? 
            WHERE file_id = ?
        """, (preco, file_id))
        conn.commit()

        bot.send_message(message.chat.id, f"Projeto '{file_name}' adicionado com sucesso por R${preco}!")
    except ValueError:
        bot.send_message(message.chat.id, "Valor inválido. Tente adicionar o projeto novamente.")

# Função para processar a compra
@bot.callback_query_handler(func=lambda call: call.data.startswith("comprar_"))
def processar_compra(call):
    projeto_id = call.data.split("_")[1]
    cursor.execute("SELECT nome, preco, file_id, usuario_id FROM projetos WHERE id = ?", (projeto_id,))
    projeto = cursor.fetchone()

    if projeto:
        nome, preco, file_id, usuario_id = projeto
        # Verifica o token do dono do produto (usuário responsável pelo produto)
        token_dono = check_token(usuario_id)
        if not token_dono:
            bot.send_message(call.message.chat.id, "O dono do produto não configurou o token do Mercado Pago.")
            return

        # Usa o token do dono do produto para criar o pagamento
        sdk_dono = SDK(token_dono[0])
        bot.send_message(call.message.chat.id, f"Você escolheu '{nome}' por R${preco}. Confirma a compra? (responda com 'sim' para continuar)")
        bot.register_next_step_handler(call.message, confirmar_pagamento, sdk_dono, projeto_id)

# Função para confirmar o pagamento e enviar o arquivo
def confirmar_pagamento(message, sdk_dono, projeto_id):
    if message.text.lower() == 'sim':
        cursor.execute("SELECT nome, preco, file_id FROM projetos WHERE id = ?", (projeto_id,))
        projeto = cursor.fetchone()

        if projeto:
            nome, preco, file_id = projeto
            # Gera pagamento PIX via Mercado Pago
            payment_data = {
                "transaction_amount": preco,
                "description": nome,
                "payment_method_id": "pix",
                "payer": {"email": "comprador@example.com"}  # Use o email real do usuário
            }
            payment_response = sdk_dono.payment().create(payment_data)
            payment_info = payment_response["response"]

            if payment_info["status"] == "pending":
                pix_code = payment_info["point_of_interaction"]["transaction_data"]["qr_code"]
                bot.send_message(message.chat.id, f"Use o QR Code ou chave PIX para pagar:\n\n{pix_code}")

                # Monitora o status do pagamento
                bot.send_message(message.chat.id, "Aguardando confirmação de pagamento...")
                while True:
                    status = sdk_dono.payment().get(payment_info["id"])["response"]["status"]
                    if status == "approved":
                        bot.send_message(message.chat.id, f"Pagamento confirmado! Enviando o projeto '{nome}'")
                        
                        # Envia o arquivo usando o file_id
                        send_file_to_user(file_id, message.chat.id)
                        bot.send_message(message.chat.id, "Projeto enviado com sucesso!")
                        break
                    elif status == "rejected":
                        bot.send_message(message.chat.id, "Pagamento não realizado. Tente novamente.")
                        break
                    time.sleep(15)
            else:
                bot.send_message(message.chat.id, "Erro no pagamento. Tente novamente.")
        else:
            bot.send_message(message.chat.id, "Produto não encontrado.")
    else:
        bot.send_message(message.chat.id, "Compra cancelada.")

# Função para iniciar o webhook
def set_webhook():
    webhook_url = os.getenv("VERCEL_URL") + '/webhook'  # Pega a URL do Vercel automaticamente
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

# Função principal para rodar o servidor Flask
# Função para lidar com as atualizações do Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True)
