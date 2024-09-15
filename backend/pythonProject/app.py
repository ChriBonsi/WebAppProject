import datetime

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
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Rotta per la registrazione
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username']
    password = data['password']

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

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Genera il token JWT
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200


# Rotta per una risorsa protetta
@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({"message": f"Welcome {current_user.username}! This is a protected route."})


# Rotta per il logout
@app.route('/logout', methods=['POST'])
def logout():
    # Implementa la logica di logout, ad esempio invalidando il token JWT
    return jsonify({"message": "Logout successful"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono già
    app.run(debug=True)

# TODO implementare hash delle password
