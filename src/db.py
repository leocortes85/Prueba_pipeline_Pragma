from sqlalchemy import Table, Column, Integer, Float, String, MetaData
from .config import engine, metadata

# Tabla principal de transacciones
transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("user_id", String, nullable=False),
    Column("unique_id", String, unique=True, nullable=False)  # para UPSERT
)

# Tabla de estadísticas incrementales
pipeline_stats = Table(
    "pipeline_stats",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("total_count", Integer, nullable=False, default=0),
    Column("sum_price", Float, nullable=False, default=0.0),
    Column("min_price", Float, nullable=True),
    Column("max_price", Float, nullable=True),
    Column("mean_price", Float, nullable=True),
    Column("last_updated", String, nullable=True)
)

# Tabla de control de archivos
file_control = Table(
    "file_control",
    metadata,
    Column("file_name", String, primary_key=True),
    Column("file_hash", String, nullable=False),
    Column("total_rows", Integer, nullable=False),
    Column("last_processed", String, nullable=True)
)


def create_tables():
    """Crear tablas en la base de datos (si no existen)."""
    metadata.create_all(engine)
    print(" Tablas creadas/verificadas: transactions, pipeline_stats, file_control")


def reset_db():
    """Vaciar tablas para reiniciar el pipeline desde cero."""
    with engine.begin() as conn:
        conn.execute(transactions.delete())
        conn.execute(pipeline_stats.delete())
        conn.execute(file_control.delete())
        conn.execute(pipeline_stats.insert().values(
            id=1, total_count=0, sum_price=0.0, min_price=None,
            max_price=None, mean_price=None, last_updated=None
        ))
    print(" Base de datos reseteada.")
