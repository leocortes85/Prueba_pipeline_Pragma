import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData

# Cargar credenciales
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Motor de conexión
engine = create_engine(DB_URL, echo=False)
metadata = MetaData()
