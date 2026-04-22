import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'greenfield-local-hub-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///greenfield.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 