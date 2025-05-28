import logging

ENABLE_LOGS = True
# Configure the logger
logging.basicConfig(
    level=logging.INFO if ENABLE_LOGS else logging.CRITICAL,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.StreamHandler()  # Log only to the console
    ]
)


logger = logging.getLogger("ProjectLogger")