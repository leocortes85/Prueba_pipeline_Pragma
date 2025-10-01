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

Creación de tablas (control_files, transactions, pipeline_stats).

Ingesta de 5 archivos CSV en microbatches (chunks).

Control de trazabilidad para evitar duplicaciones en la ingesta

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

| Columna   | Tipo                      | Descripción                                                                                          |
| --------- | ------------------------- | ---------------------------------------------------------------------------------------------------- |
| id        | INT (PK, autoincremental) | Identificador único interno.                                                                         |
| timestamp | STRING                    | Fecha/hora del evento en formato ISO (`YYYY-MM-DD HH:MM:SS`).                                        |
| price     | FLOAT                     | Valor numérico de la transacción.                                                                    |
| user_id   | STRING                    | Identificador del usuario.                                                                           |
| unique_id | STRING (UNIQUE)           | Clave técnica generada como `timestamp_user_id`, usada para evitar duplicados y permitir **UPSERT**. |

---

### pipeline_stats

Mantiene una sola fila con estadísticas acumuladas e incrementales.

| Columna      | Tipo                | Descripción                                |
| ------------ | ------------------- | ------------------------------------------ |
| id           | INT (PK, fijo en 1) | Identificador único de la fila de stats.   |
| total_count  | INT                 | Número total de registros procesados.      |
| sum_price    | FLOAT               | Suma acumulada de todos los `price`.       |
| min_price    | FLOAT               | Precio mínimo observado.                   |
| max_price    | FLOAT               | Precio máximo observado.                   |
| mean_price   | FLOAT               | Promedio (`sum_price / total_count`).      |
| last_updated | STRING              | Fecha/hora ISO de la última actualización. |

---

### file_control

Tabla de control de archivos procesados, utilizada para trazabilidad e idempotencia.

| Columna        | Tipo        | Descripción                                                 |
| -------------- | ----------- | ----------------------------------------------------------- |
| file_name      | STRING (PK) | Nombre del archivo procesado.                               |
| file_hash      | STRING      | Hash MD5 del contenido del archivo (para detectar cambios). |
| total_rows     | INT         | Número de filas procesadas del archivo.                     |
| last_processed | STRING      | Fecha/hora ISO de la última vez que el archivo fue cargado. |

---

Con este esquema el pipeline asegura:

- **Escalabilidad** → procesamiento por microbatches.
- **Idempotencia** → `unique_id` + `UPSERT` evitan duplicados.
- **Trazabilidad** → `file_control` registra qué archivos se cargaron y cuándo.
- **Estadísticas incrementales** → `pipeline_stats` se actualiza sin recalcular todo desde cero.

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
