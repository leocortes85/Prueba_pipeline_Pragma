# Prueba de Ingeniería de Datos – Pipeline por Microbatches

Este proyecto implementa un **pipeline de datos** que ingiere archivos CSV en **microbatches**, los inserta en PostgreSQL y mantiene estadísticas **incrementales** en tiempo real (`count`, `mean`, `min`, `max`) sin recalcular sobre toda la tabla.

El entregable incluye:

1. Un **notebook ejecutable** (`notebooks/NB_PIPELINE_PRAGMA.ipynb`) con todo el desarrollo paso a paso.
2. Un **repositorio modular** (`src/`, `scripts/`) que simula un entorno productivo.

---

## 📂 Estructura del proyecto

Este proyecto sigue una organización modular para pruebas de ingeniería de datos, facilitando la lectura, pruebas y mantenimiento.

# Generando el formato correcto para el README.md

prueba-ingeniero-datos/

├── data/ # Archivos CSV de entrada (2012-1.csv ... validation.csv)

├── notebooks/

│ └── pipeline.ipynb # Notebook principal para la prueba

├── src/ # Código modular estilo productivo

│ ├── **init**.py

│ ├── config.py # Configuración de conexión (.env, SQLAlchemy)

│ ├── db.py # Definición de tablas y funciones de reset

│ ├── stats.py # Funciones de actualización de estadísticas

│ └── pipeline.py # Lógica principal de ingesta por microbatches

├── scripts/

│ └── run_pipeline.py # Script CLI para ejecutar el pipeline completo

├── tests/

│ └── test_stats.py # Prueba unitaria simple

├── .env # Variables de entorno

├── requirements.txt # Dependencias del proyecto

└── README.md # Este archivo

### Notas

- Los archivos bajo `src/` contienen la lógica reusable y modular.
- `notebooks/` es solo para exploración, documentación de pruebas y experimentación.
- `scripts/` permite ejecutar el pipeline completo desde la terminal sin abrir el notebook.
- `tests/` contiene pruebas unitarias básicas para asegurar la integridad de funciones críticas.
- `.env` y `requirements.txt` facilitan la configuración del entorno y la instalación de dependencias.

---

## ⚙️ Requisitos

- Python 3.11+
- Docker
- PostgreSQL 15 (se recomienda usar Docker)

Instalar dependencias:

pip install -r requirements.txt

---

## Levantar PostgreSQL con Docker

docker run --name prueba-postgres \
 -e POSTGRES_USER=username \
 -e POSTGRES_PASSWORD=password \
 -e POSTGRES_DB=db_name \
 -p 5432:5432 \
 -d postgres:15

Verificar que el contenedor esté corriendo:

docker ps

## Configuración de variables de entorno

Copiar el archivo .env.example a .env y ajustar las credenciales:

DB_USER=username
DB_PASS=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_name

---

## 📒 Ejecución del Notebook

Abrir el archivo:
notebooks/pipeline.ipynb

En el notebook encontrarás:

Creación de tablas (transactions, pipeline_stats).

Ingesta de 5 archivos CSV en microbatches (chunks).

Actualización incremental de estadísticas.

Validación con validation.csv.

Consultas de verificación tanto en Python como en SQL puro.

## Ejecución modular (estilo productivo)

El repo incluye la lógica separada en módulos (src/) y un script de orquestación (scripts/run_pipeline.py).

Para ejecutar todo el pipeline desde consola:

python scripts/run_pipeline.py

Esto:

Crea las tablas en PostgreSQL.

Reinicia el estado de la base (TRUNCATE + fila inicial en pipeline_stats).

Procesa los 5 archivos CSV de entrenamiento.

Procesa el archivo de validación.

Imprime estadísticas actualizadas por cada chunk.

## Pruebas unitarias

El directorio tests/ contiene una prueba básica (pytest) para validar la función de actualización de estadísticas:

pytest tests/

## Tablas utilizadas

### transactions

Almacena cada transacción fila por fila.

id (PK, autoincremental)

timestamp (string en formato ISO)

price (float)

user_id (string)

### pipeline_stats

Mantiene una sola fila con estadísticas incrementales.

id (PK, fijo en 1)

total_count

sum_price

min_price

max_price

mean_price

last_updated

## Consideraciones

Aunque los archivos CSV del reto tienen pocas filas (máx. ~40), el pipeline se diseñó con microbatches (chunksize) para simular un escenario real de Big Data, evitando cargar todo en memoria.

Se proveen dos enfoques de consulta:

Python/pandas → integración directa con DataFrames.

SQL puro con %sql → consultas ligeras, sin consumir memoria adicional.

## 🎯 Conclusión

Este proyecto demuestra:

Diseño de pipelines de ingesta por microbatches.

Uso de SQLAlchemy para modelado de tablas y transacciones.

Manejo de estadísticas incrementales.

Buenas prácticas de modularización (separación en src/, scripts/, tests/).

Entrega en dos formatos: notebook ejecutable y repo productivo.
