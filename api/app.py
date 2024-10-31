from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

# Variável para armazenar o tempo de expiração
expiration_time = None

@app.route('/temp', methods=['GET'])
def temp_status():
    global expiration_time
    
    # Obter os valores dos parâmetros da URL, usando 0 como padrão caso não sejam fornecidos
    try:
        dias = int(request.args.get('dia', 0))         # Parâmetro 'dia' (padrão 0)
        horas = int(request.args.get('hora', 0))        # Parâmetro 'hora' (padrão 0)
        minutos = int(request.args.get('minuto', 0))    # Parâmetro 'minuto' (padrão 0)
        segundos = int(request.args.get('segundo', 0))  # Parâmetro 'segundo' (padrão 0)
    except ValueError:
        return jsonify({"error": "Parâmetro inválido"}), 400  # Código HTTP 400 para erro de requisição
    
    # Se não houver um tempo de expiração definido, configurá-lo com base nos parâmetros fornecidos
    if expiration_time is None:
        expiration_time = datetime.now() + timedelta(days=dias, hours=horas, minutes=minutos, seconds=segundos)
    
    # Calcular o tempo restante até expirar
    now = datetime.now()
    time_remaining = expiration_time - now
    
    if time_remaining.total_seconds() <= 0:
        return jsonify({"message": "Expirado"}), 410  # Código HTTP 410 para recurso expirado
    
    # Formatar o tempo restante em dias, horas, minutos e segundos
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return jsonify({
        "message": "Ativo",
        "tempo_restante": {
            "dias": days,
            "horas": hours,
            "minutos": minutes,
            "segundos": seconds
        }
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
