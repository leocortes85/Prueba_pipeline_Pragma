import pandas as pd
from sqlalchemy import text
from src.config import engine
from src.db import transactions
from src.stats import update_stats_db

def process_csv_file(file_path, chunk_size=10, update_per="chunk"):
    """
    Procesa un CSV en microbatches y actualiza la BD.
    """
    print(f"\n📂 Procesando archivo: {file_path}")
    reader = pd.read_csv(file_path, chunksize=chunk_size)

    total_chunks = 0
    for chunk in reader:
        total_chunks += 1
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')
        chunk = chunk.dropna(subset=['timestamp', 'price', 'user_id'])
        if chunk.empty:
            continue

        chunk['timestamp'] = chunk['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        chunk['price'] = pd.to_numeric(chunk['price'], errors='coerce')
        chunk = chunk.dropna(subset=['price'])
        if chunk.empty:
            continue

        records = chunk.to_dict(orient="records")

        chunk_count = len(records)
        chunk_sum = float(chunk["price"].sum())
        chunk_min = float(chunk["price"].min())
        chunk_max = float(chunk["price"].max())

        with engine.begin() as conn:
            conn.execute(transactions.insert(), records)
            if update_per == "row":
                for r in records:
                    update_stats_db(conn, 1, r["price"], r["price"], r["price"])
            else:
                update_stats_db(conn, chunk_count, chunk_sum, chunk_min, chunk_max)

        with engine.connect() as conn2:
            stats_row = conn2.execute(
                text("SELECT total_count, mean_price, min_price, max_price FROM pipeline_stats WHERE id=1")
            ).fetchone()
            print(f"  Chunk {total_chunks} → count={stats_row[0]}, mean={stats_row[1]}, min={stats_row[2]}, max={stats_row[3]}")

    print(f"✅ Finalizado archivo: {file_path} ({total_chunks} chunks)")
