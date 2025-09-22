import mysql.connector
from contextlib import contextmanager
from game import config

# Yleiset database asetukset
# user, password, host, port ladataan dotenv kirjaston avulla projektin .env filestä
# charset, collation ja autocommit hard koodattu
DB_CONFIG = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "port": config.DB_PORT,
    "database": config.DB_NAME,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
}


# Yleinen database connection methodi
# https://docs.python.org/3/library/contextlib.html
@contextmanager
def get_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()
