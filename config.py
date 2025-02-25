import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "postgresql://expense_tracker_db_19k7_user:CRz1nz2t9sOPtoPNK8y7WTFvLUNAf0lM@dpg-cuur6dqj1k6c73a1897g-a.oregon-postgres.render.com/expense_tracker_db_19k7")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token expires in 1 hour
