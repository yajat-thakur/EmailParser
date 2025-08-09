import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST =os.getenv("DB_HOST")
    DB_PORT= int(os.getenv("DB_PORT"))
    DB_USER= os.getenv("DB_USER")
    DB_PASSWORD=os.getenv("DB_PASSWORD")
    DB_NAME=os.getenv("DB_NAME")

settings=Settings()
