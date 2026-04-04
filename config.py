class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret-key'