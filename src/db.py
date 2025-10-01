from sqlalchemy import Table, Column, Integer, Float, String, text
from src.config import engine, metadata

# Tabla de transacciones
transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("user_id", String, nullable=False),
)

# Tabla de estadísticas acumuladas
pipeline_stats = Table(
    "pipeline_stats",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("total_count", Integer, nullable=False, default=0),
    Column("sum_price", Float, nullable=False, default=0.0),
    Column("min_price", Float, nullable=True),
    Column("max_price", Float, nullable=True),
    Column("mean_price", Float, nullable=True),
    Column("last_updated", String, nullable=True),
)

def create_tables():
    metadata.create_all(engine)
    print("✅ Tablas creadas en la base de datos.")

def reset_db():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_stats RESTART IDENTITY CASCADE;"))
        conn.execute(text("""
            INSERT INTO pipeline_stats (id, total_count, sum_price, min_price, max_price, mean_price, last_updated)
            VALUES (1, 0, 0.0, NULL, NULL, NULL, now())
        """))
    print("✅ Tablas truncadas y reinicializadas.")
