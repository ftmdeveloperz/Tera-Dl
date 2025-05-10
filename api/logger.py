# api/logger.py

import logging
import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging
logger = logging.getLogger("TeraboxAPI")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("logs/api.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Console handler (optional: shows logs in terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
