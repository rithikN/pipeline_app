# utils/configure_app.py - Central config
from dotenv import load_dotenv
import os

load_dotenv()  # Load once at app start

class Config:
    PIPELINE_ENV = os.getenv('PIPELINE_ENV')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


