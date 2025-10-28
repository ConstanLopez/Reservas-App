import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_USER = os.getenv('DB_USER', 'appuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'apppass')
    DB_NAME = os.getenv('DB_NAME', 'reservas_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))
