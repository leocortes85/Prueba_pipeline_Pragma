from sqlalchemy import text

def update_stats_db(conn, chunk_count, chunk_sum, chunk_min, chunk_max):
    row = conn.execute(text("SELECT total_count, sum_price, min_price, max_price FROM pipeline_stats WHERE id=1")).fetchone()
    old_count = int(row[0]) if row and row[0] is not None else 0
    old_sum = float(row[1]) if row and row[1] is not None else 0.0
    old_min = float(row[2]) if row and row[2] is not None else float("inf")
    old_max = float(row[3]) if row and row[3] is not None else float("-inf")

    new_count = old_count + int(chunk_count)
    new_sum = old_sum + float(chunk_sum)
    new_min = min(old_min, float(chunk_min))
    new_max = max(old_max, float(chunk_max))
    new_mean = new_sum / new_count if new_count > 0 else None

    conn.execute(text("""
        UPDATE pipeline_stats
        SET total_count = :new_count,
            sum_price = :new_sum,
            min_price = :new_min,
            max_price = :new_max,
            mean_price = :new_mean,
            last_updated = now()
        WHERE id = 1
    """), {
        "new_count": new_count,
        "new_sum": new_sum,
        "new_min": new_min,
        "new_max": new_max,
        "new_mean": new_mean
    })

    return {"count": new_count, "min": new_min, "max": new_max, "mean": new_mean}
