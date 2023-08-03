import psycopg2
from config import config
# PostgreSQL configuration
pg_config = {
    'dbname': config['db_name'],
    'user': config['db_user'],
    'password': config['db_pwd'],
    'host': config['db_host'],
}

def create_postgres_connection():
    try:
        connection = psycopg2.connect(**pg_config)
        return connection
    except Exception as e:
        raise ConnectionError("Failed to connect to PostgreSQL")
