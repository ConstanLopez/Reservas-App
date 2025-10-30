import os #Modulo de python para acceder a variables del sistema
from dotenv import load_dotenv #Modulo que sirve para cargar variables desde un archivo .env
load_dotenv() #busca un archivo .env en el directorio del proyecto y carga sus valores en el entorno

class Config:
    #Definimos para cada variable un  default, por si el el nombre de la 'clave' no esta en el .env
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_USER = os.getenv('DB_USER', 'appuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'apppass')
    DB_NAME = os.getenv('DB_NAME', 'reservas_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))
