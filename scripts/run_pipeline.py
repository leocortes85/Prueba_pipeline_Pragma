import glob, os, re
from src.db import create_tables, reset_db
from src.pipeline import process_csv_file

def main():
    print(" Iniciando pipeline")
    create_tables()
    reset_db()

    # Buscar CSVs en carpeta data/
    data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
    all_csv = glob.glob(os.path.join(data_folder, "*.csv"))

    def sort_key(path):
        name = os.path.basename(path)
        nums = re.findall(r'\d+', name)
        return tuple(map(int, nums)) if nums else (9999,)

    all_csv_sorted = sorted(all_csv, key=sort_key)
    train_files = [f for f in all_csv_sorted if "validation" not in f.lower()]
    validation_file = [f for f in all_csv_sorted if "validation" in f.lower()][0]

    print("\n Archivos de entrenamiento:")
    for f in train_files:
        print(" -", os.path.basename(f))

    for f in train_files:
        process_csv_file(f, chunk_size=10, update_per='chunk')

    print("\n Archivo de validación:")
    print(" -", os.path.basename(validation_file))
    process_csv_file(validation_file, chunk_size=10, update_per='chunk')

    print("\n Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
