from sqlalchemy import text
import datetime

def update_stats_db(conn, count, sum_price, min_price, max_price):
    """
    Actualiza la fila de estadísticas incrementales en pipeline_stats.
    Usa sumatoria incremental en lugar de recalcular todo.
    """
    row = conn.execute(text("SELECT total_count, sum_price, min_price, max_price FROM pipeline_stats WHERE id=1")).fetchone()
    if not row:
        conn.execute(text("""
            INSERT INTO pipeline_stats (id, total_count, sum_price, min_price, max_price, mean_price, last_updated)
            VALUES (1, :count, :sum_price, :min_price, :max_price, :mean_price, :last_updated)
        """), {
            "count": count,
            "sum_price": sum_price,
            "min_price": min_price,
            "max_price": max_price,
            "mean_price": sum_price / count if count > 0 else None,
            "last_updated": datetime.datetime.now().isoformat()
        })
    else:
        prev_count, prev_sum, prev_min, prev_max = row
        new_count = prev_count + count
        new_sum = prev_sum + sum_price
        new_min = min(filter(lambda x: x is not None, [prev_min, min_price]))
        new_max = max(filter(lambda x: x is not None, [prev_max, max_price]))
        new_mean = new_sum / new_count if new_count > 0 else None

        conn.execute(text("""
            UPDATE pipeline_stats
            SET total_count=:count,
                sum_price=:sum,
                min_price=:min,
                max_price=:max,
                mean_price=:mean,
                last_updated=:last_updated
            WHERE id=1
        """), {
            "count": new_count,
            "sum": new_sum,
            "min": new_min,
            "max": new_max,
            "mean": new_mean,
            "last_updated": datetime.datetime.now().isoformat()
        })
