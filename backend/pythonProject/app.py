import datetime
import re
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione dell'app
app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia questa chiave in produzione
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:db_password@localhost:5432/webapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inizializzazione del database
db = SQLAlchemy(app)


# Modello utente
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


# Funzione per verificare il token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')  # Usa Authorization header

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        token = token.replace("Bearer ", "")  # Rimuove "Bearer" dal token

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Funzione per validare input
def validate_input(username, password):
    if not re.match("^[a-zA-Z0-9_.-]+$", username):
        return "Invalid username format. Only alphanumeric characters, dots, underscores, and hyphens are allowed."
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    return None


# Rotta per la registrazione
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Controllo se mancano campi o sono vuoti
    if 'username' not in data or not data['username'].strip() or 'password' not in data or not data['password'].strip():
        return jsonify({"message": "Missing or empty username or password"}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    # Validazione lato server
    validation_error = validate_input(username, password)
    if validation_error:
        return jsonify({"message": validation_error}), 400

    # Controlla se l'username esiste già
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# Rotta per il login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Controllo se mancano campi o sono vuoti
    if 'username' not in data or not data['username'].strip() or 'password' not in data or not data['password'].strip():
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    # Validazione lato server
    validation_error = validate_input(username, password)
    if validation_error:
        return jsonify({"message": validation_error}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Genera il token JWT con durata 30 minuti
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200


# Rotta per una risorsa protetta
@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({"message": f"Welcome {current_user.username}! This is a protected route."})


# Rotta per il logout (per cancellare il token lato client)
@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono già
    app.run(debug=True)
