from dotenv import load_dotenv
import os

# Retrieves secret key from env var
load_dotenv()
secret_key = os.environ.get("APP_SECRET_KEY")
