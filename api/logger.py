import logging
import os

# Check if the environment is Lambda or similar, or use a local temporary directory
log_dir = '/tmp'  # Writable location for Lambda, or choose another location for your environment
log_file_path = os.path.join(log_dir, 'api.log')

# Create a logger instance
logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)

# Create file handler to write logs to a file in the writable directory
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create a console handler to log to console as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Set the log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Log something to test
logger.info("Logging setup completed")
