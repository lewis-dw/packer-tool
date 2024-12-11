import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # get environment variables
    prefix = os.getenv('DB_PREFIX')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')

    # SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = f"{prefix}://{username}:{password}@{host}:{port}/{name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False