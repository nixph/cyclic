import os
from dotenv import load_dotenv

load_dotenv()

# Read the variable from the environment (or .env file)
bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")

print(" MAIN PROGRAM INITIALIZED")
