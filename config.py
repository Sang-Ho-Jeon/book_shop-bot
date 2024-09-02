import os

class Config:
    def __init__(self):
        self.OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
        self.OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')
        self.SPRING_SERVER_URL = os.getenv('SPRING_SERVER_URL')
        self.DATABASE_USERID = os.getenv('DATABASE_USERID')
        self.DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
        self.DATABASE_HOST = os.getenv('DATABASE_HOST')
        self.DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA')
