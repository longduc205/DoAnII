"""
Application Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///scanner.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Scanner settings
    CRAWL_MAX_DEPTH = int(os.getenv('CRAWL_MAX_DEPTH', 3))
    CRAWL_MAX_PAGES = int(os.getenv('CRAWL_MAX_PAGES', 50))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    SCAN_DELAY = float(os.getenv('SCAN_DELAY', 0.5))

    # AI Module settings
    AI_MODEL_PATH = os.getenv('AI_MODEL_PATH', 'ai/models/classifier.pkl')
    AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', 0.7))
