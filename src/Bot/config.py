import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
    MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTENT_MESSAGES", 10))
    DB_URL = os.getenv("DB_URL")
    
    if not BOT_TOKEN or not OPEN_API_KEY:
        raise ValueError("Не найдены BOT_TOKEN и OPEN_API_KEY, настройте их в файле .env")
    
    if not DB_URL:
        raise ValueError("Не найдена DB_URL, настройте его в файле .env")


config = Config()

