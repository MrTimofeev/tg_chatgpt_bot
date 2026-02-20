import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # TG
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # OPENAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    
    MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", 10))
    
    
    DB_URL = os.getenv("DB_URL")
    
    if not BOT_TOKEN:
        raise ValueError("Не найден BOT_TOKEN, настройте его в файле .env")

    if not OPENAI_API_KEY:
        raise ValueError("Не найден OPENAI_API_KEY, настройте его в файле .env")
    
    if not DB_URL:
        raise ValueError("Не найдена DB_URL, настройте его в файле .env")


config = Config()

