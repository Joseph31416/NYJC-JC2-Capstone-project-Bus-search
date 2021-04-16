from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.environ.get("APP_SECRET_KEY")
