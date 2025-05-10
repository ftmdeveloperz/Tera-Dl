import logging

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Console handler (prints to stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

logger.info("Logger initialized successfully.")
