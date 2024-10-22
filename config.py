class Config:
    # SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pwd@localhost:5432/testy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

    # postgres
    # pwd
    # 5432