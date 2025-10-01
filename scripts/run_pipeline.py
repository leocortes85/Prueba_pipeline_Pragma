import glob, os, re
from src.db import create_tables, reset_db
from src.pipeline import process_csv_file

def sort_key(path):
    name = os.path.basename(path)
    nums = re.findall(r'\d+', name)
    return tuple(map(int, nums)) if nums else (9999,)

if __name__ == "__main__":
    data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
    all_csv = glob.glob(os.path.join(data_folder, "*.csv"))
    all_csv_sorted = sorted(all_csv, key=sort_key)

    train_files = [f for f in all_csv_sorted if "validation" not in os.path.basename(f).lower()]
    validation_file = next((f for f in all_csv_sorted if "validation" in os.path.basename(f).lower()), None)

    print("🚀 Iniciando pipeline...")
    create_tables()
    reset_db()

    for f in train_files:
        process_csv_file(f, chunk_size=10)

    if validation_file:
        print("\n📂 Procesando archivo de validación...")
        process_csv_file(validation_file, chunk_size=10)

    print("\n🎉 Pipeline completado.")
