import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
# OUTLOOK_CLIENT_ID = os.getenv('OUTLOOK_CLIENT_ID')
# OUTLOOK_CLIENT_SECRET = os.getenv('OUTLOOK_CLIENT_SECRET')
# OUTLOOK_TENANT_ID = os.getenv('OUTLOOK_TENANT_ID', 'common')

# Ollama Configuration
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"


# Application Settings
MAX_EMAILS_TO_FETCH = 10
EMAIL_SUMMARY_MAX_LENGTH = 200 