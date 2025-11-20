# test_mysql.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

try:
    cn = mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST') or '127.0.0.1',
        database=os.getenv('DB_NAME')
    )
    print("Connected:", cn.is_connected())
    cn.close()
except Error as e:
    print("ERROR:", e)
