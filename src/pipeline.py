import os, hashlib, pandas as pd
from sqlalchemy import insert, text
from .config import engine
from .db import transactions, file_control
from .stats import update_stats_db


# --- Funciones auxiliares para control de archivos ---

def file_hash(file_path):
    """Devuelve hash MD5 del archivo completo."""
    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def should_process_file(file_path):
    """Decide si un archivo debe procesarse según file_control."""
    fname = os.path.basename(file_path)
    fhash = file_hash(file_path)
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT file_hash, total_rows FROM file_control WHERE file_name=:fname"),
            {"fname": fname}
        ).fetchone()
    if row is None:
        return True, fhash, None
    elif row[0] != fhash:
        return True, fhash, row[1]  # modificado
    else:
        return False, fhash, row[1]  # sin cambios


# --- Función principal del pipeline ---

def process_csv_file(file_path, chunk_size=10, update_per='chunk'):
    """
    Procesa un archivo CSV en microbatches (chunks).
    Inserta los registros en 'transactions' y actualiza la fila 'pipeline_stats' incrementalmente.
    Usa file_control para evitar reprocesar archivos sin cambios.
    """
    fname = os.path.basename(file_path)
    process, fhash, prev_rows = should_process_file(file_path)
    if not process:
        print(f" Archivo '{fname}' ya procesado y sin cambios. Se omite.")
        return

    print(f"\n Procesando archivo: {fname}")
    reader = pd.read_csv(file_path, chunksize=chunk_size)
    total_chunks, total_records = 0, 0

    for chunk in reader:
        total_chunks += 1

        # --- limpieza / transformaciones ---
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')
        chunk = chunk.dropna(subset=['timestamp', 'price', 'user_id'])
        if chunk.empty:
            continue

        chunk['timestamp'] = chunk['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        chunk['price'] = pd.to_numeric(chunk['price'], errors='coerce')
        chunk = chunk.dropna(subset=['price'])
        if chunk.empty:
            continue

        #  Asegurar que user_id sea string antes de armar el unique_id
        chunk['user_id'] = chunk['user_id'].astype(str)

        # Generar unique_id (ej: "2025-09-30 10:00:00_12345")
        chunk['unique_id'] = chunk['timestamp'] + "_" + chunk['user_id']

        # convertir a lista de dicts para insertar
        records = chunk.to_dict(orient='records')
        total_records += len(records)

        # calcular stats del chunk
        chunk_count = len(records)
        chunk_sum = float(chunk['price'].sum())
        chunk_min = float(chunk['price'].min())
        chunk_max = float(chunk['price'].max())

        # --- inserción y actualización ---
        with engine.begin() as conn:
            # UPSERT en transactions
            for r in records:
                stmt = insert(transactions).values(r)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['unique_id'],
                    set_={
                        "timestamp": stmt.excluded.timestamp,
                        "price": stmt.excluded.price,
                        "user_id": stmt.excluded.user_id
                    }
                )
                conn.execute(stmt)

            # actualización de stats
            if update_per == 'row':
                for r in records:
                    update_stats_db(conn, 1, r['price'], r['price'], r['price'])
            else:
                update_stats_db(conn, chunk_count, chunk_sum, chunk_min, chunk_max)

    # --- registrar archivo en file_control ---
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO file_control (file_name, file_hash, total_rows, last_processed)
                VALUES (:fname, :fhash, :total_rows, now())
                ON CONFLICT (file_name) DO UPDATE
                SET file_hash=:fhash,
                    total_rows=:total_rows,
                    last_processed=now()
            """),
            {"fname": fname, "fhash": fhash, "total_rows": total_records}
        )

    print(f" Finalizado archivo: {fname}. Chunks: {total_chunks}, Filas procesadas: {total_records}")
