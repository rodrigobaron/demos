from pathlib import Path
from configparser import ConfigParser
from pgvector.psycopg import register_vector
import psycopg

def db_config(filename: Path = "database.ini", section: str = 'postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        params = parser.items(section)
        db = {param[0]: param[1] for param in params}
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db

def get_connection():
    params = db_config()
    conn = psycopg.connect(**params, autocommit=True)
    conn.execute('CREATE EXTENSION IF NOT EXISTS vector')

    register_vector(conn)
    return conn
