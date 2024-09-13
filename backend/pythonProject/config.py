class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:db_password@localhost/webapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'  # Cambia questa chiave in produzione
