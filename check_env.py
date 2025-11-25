from dotenv import load_dotenv
import os

load_dotenv()

print("cwd:", os.getcwd())
print("Found .env:", os.path.exists('.env'))
print("USE_LOCAL_MYSQL:", os.getenv('USE_LOCAL_MYSQL'))
print("DB_HOST:", os.getenv('DB_HOST'))
print("DB_USER:", os.getenv('DB_USER'))
print("DB_PASS:", os.getenv('DB_PASS'))
print("DB_NAME:", os.getenv('DB_NAME'))
print("DATABASE_URL:", os.getenv('DATABASE_URL'))
