import datetime

import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione dell'app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia questa chiave in produzione
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:db_password@localhost:5432/webapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inizializzazione del database
db = SQLAlchemy(app)

# Configura Limiter per prevenire attacchi brute-force
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


# Modello utente
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)


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

    if 'username' not in data or not data['username'].strip() or 'password' not in data or not data['password'].strip():
        return jsonify({"message": "Missing or empty username or password"}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    # Controlla se l'username esiste già
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


def is_account_locked(user):
    if user.account_locked_until:
        if datetime.datetime.now() < user.account_locked_until:
            return True
        else:
            # Sblocca l'account se il tempo è trascorso
            user.failed_login_attempts = 0
            user.account_locked_until = None
            db.session.commit()
    return False


@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Limita a 5 tentativi di login per IP al minuto
def login():
    data = request.get_json()

    if 'username' not in data or not data['username'].strip() or 'password' not in data or not data['password'].strip():
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    # Controlla se l'account è bloccato
    if user.account_locked_until and datetime.datetime.now() < user.account_locked_until:
        return jsonify({"message": "Account is temporarily locked due to multiple failed login attempts."}), 403

    # Se il tempo di blocco è trascorso, sblocca l'account
    if user.account_locked_until and datetime.datetime.now() >= user.account_locked_until:
        user.failed_login_attempts = 0
        user.account_locked_until = None
        db.session.commit()

    # Verifica la password
    if not check_password_hash(user.password, password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.account_locked_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
        db.session.commit()
        return jsonify({"message": "Invalid username or password"}), 401

    # Reset dei tentativi falliti dopo un login corretto
    user.failed_login_attempts = 0
    user.account_locked_until = None
    db.session.commit()

    # Genera il token JWT
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono già
    app.run(debug=True)
