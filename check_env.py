# check_env.py
import os
from dotenv import load_dotenv

load_dotenv()   # loads .env from cwd

print("cwd:", os.getcwd())
print("Found .env file?:", os.path.exists('.env'))
print("USE_LOCAL_MYSQL =", os.getenv('USE_LOCAL_MYSQL'))
print("DB_HOST         =", os.getenv('DB_HOST'))
print("DB_USER         =", os.getenv('DB_USER'))
print("DB_PASS         =", os.getenv('DB_PASS'))
print("DB_NAME         =", os.getenv('DB_NAME'))
print("DATABASE_URL env=", os.getenv('DATABASE_URL'))

# replicate your app logic
DATABASE_URL = os.getenv('DATABASE_URL')
USE_LOCAL_MYSQL = os.getenv('USE_LOCAL_MYSQL', '0') == '1'

if not DATABASE_URL and USE_LOCAL_MYSQL:
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'covid_beds')
    DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///local_dev.db'

print("Final DATABASE_URL =", DATABASE_URL)
