from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione dell'app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:db_password@localhost:5432/webapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inizializzazione del database
db = SQLAlchemy(app)


# Modello utente
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


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

    # Qui dovresti generare e restituire un token JWT

    return jsonify({"message": "Login successful"}), 200


# Rotta per il logout
@app.route('/logout', methods=['POST'])
def logout():
    # Implementa la logica di logout, ad esempio invalidando il token JWT
    return jsonify({"message": "Logout successful"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono già
    app.run(debug=True)

# TODOD implementare hash delle password
