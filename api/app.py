from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://default:tkOBoc47UaCg@ep-cool-snowflake-790363.us-west-2.aws.neon.tech:5432/verceldb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definição de um modelo de exemplo
class Timer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)  # ID do usuário
    expiration_time = db.Column(db.DateTime, nullable=False)  # Hora de expiração

    def __repr__(self):
        return f'<Timer {self.id} - User {self.user_id}>'

# Rota para criar um novo timer para um usuário
@app.route('/add_timer', methods=['POST'])
def add_timer():
    data = request.json
    user_id = data.get('user_id')
    
    # Obter os valores de tempo
    dias = int(data.get('dias', 0))
    horas = int(data.get('horas', 0))
    minutos = int(data.get('minutos', 0))
    segundos = int(data.get('segundos', 0))
    
    # Calcular o tempo de expiração
    expiration_time = datetime.now() + timedelta(days=dias, hours=horas, minutes=minutos, seconds=segundos)
    
    # Criar o novo timer
    new_timer = Timer(user_id=user_id, expiration_time=expiration_time)
    db.session.add(new_timer)
    db.session.commit()
    
    return jsonify({"message": "Timer adicionado com sucesso!", "id": new_timer.id}), 201

# Rota para obter o timer de um usuário
@app.route('/timer/<user_id>', methods=['GET'])
def get_user_timer(user_id):
    timer = Timer.query.filter_by(user_id=user_id).first()
    
    if timer is None:
        return jsonify({"message": "Nenhum timer encontrado para este usuário."}), 404
    
    # Calcular o tempo restante até expirar
    time_remaining = timer.expiration_time - datetime.now()
    
    if time_remaining.total_seconds() <= 0:
        return jsonify({"message": "Expirado"}), 410  # Código HTTP 410 para recurso expirado

    # Formatar o tempo restante em dias, horas, minutos e segundos
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return jsonify({
        "user_id": user_id,
        "tempo_restante": {
            "dias": days,
            "horas": hours,
            "minutos": minutes,
            "segundos": seconds
        }
    })

# Rota para inicializar o banco de dados
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
