"""
Script de inicialización / seed de la base de datos de Lumi.

Crea la tabla `places` (si no existe) y carga los lugares turísticos
base. Es seguro ejecutarlo varias veces: por defecto usa UPSERT (inserta
o actualiza por nombre) en vez de borrar y reinsertar todo, así no se
rompen relaciones ni se reciclan IDs innecesariamente.

Uso:
    python seed_database.py            # inserta/actualiza sin borrar nada
    python seed_database.py --reset    # borra todos los lugares y los vuelve a insertar
"""

import argparse
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

# Ruta absoluta basada en la ubicación del script, para que funcione sin
# importar desde qué carpeta se ejecute.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "lumi.db"

VALID_CATEGORIES = {"museo", "parque", "mirador"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Datos base (fácil de extender: solo agregar un diccionario a la lista)
# ---------------------------------------------------------------------------

PLACES = [
    {
        "name": "Monserrate",
        "category": "mirador",
        "description": "Uno de los lugares turísticos más visitados de Bogotá.",
        "schedule": "Lunes a Domingo 5:00 AM - 10:00 PM",
        "latitude": 4.6057,
        "longitude": -74.0566,
        "image": "monserrate.jpg",
    },
    {
        "name": "Museo del Oro",
        "category": "museo",
        "description": "Museo con una de las colecciones de oro prehispánico más importantes del mundo.",
        "schedule": "Martes a Domingo 9:00 AM - 5:00 PM",
        "latitude": 4.6019,
        "longitude": -74.0723,
        "image": "museo_oro.jpg",
    },
    {
        "name": "Jardín Botánico",
        "category": "parque",
        "description": "Espacio natural con una gran diversidad de flora colombiana.",
        "schedule": "8:00 AM - 5:00 PM",
        "latitude": 4.6676,
        "longitude": -74.1048,
        "image": "jardin_botanico.jpg",
    },
]


# ---------------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------------

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (category IN ({",".join(f"'{c}'" for c in VALID_CATEGORIES)})),
    description TEXT NOT NULL,
    schedule TEXT NOT NULL,
    latitude REAL CHECK (latitude BETWEEN -90 AND 90),
    longitude REAL CHECK (longitude BETWEEN -180 AND 180),
    image TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

INDEX_CATEGORY = "CREATE INDEX IF NOT EXISTS idx_places_category ON places(category)"

UPSERT_SQL = """
INSERT INTO places (name, category, description, schedule, latitude, longitude, image)
VALUES (:name, :category, :description, :schedule, :latitude, :longitude, :image)
ON CONFLICT(name) DO UPDATE SET
    category = excluded.category,
    description = excluded.description,
    schedule = excluded.schedule,
    latitude = excluded.latitude,
    longitude = excluded.longitude,
    image = excluded.image,
    updated_at = CURRENT_TIMESTAMP
"""


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

def validate_place(place):
    """
    Valida que un registro de lugar tenga todos los campos requeridos y
    valores dentro de rangos razonables. Lanza ValueError si algo está mal,
    para detectar errores de datos antes de tocar la base de datos.
    """
    required_fields = {
        "name", "category", "description", "schedule",
        "latitude", "longitude", "image",
    }
    missing = required_fields - place.keys()
    if missing:
        raise ValueError(f"Lugar '{place.get('name', '?')}' no tiene los campos: {missing}")

    if not place["name"].strip():
        raise ValueError("El nombre del lugar no puede estar vacío.")

    if place["category"] not in VALID_CATEGORIES:
        raise ValueError(
            f"Categoría inválida '{place['category']}' en '{place['name']}'. "
            f"Debe ser una de: {VALID_CATEGORIES}"
        )

    lat, lng = place["latitude"], place["longitude"]
    if lat is not None and not (-90 <= lat <= 90):
        raise ValueError(f"Latitud fuera de rango en '{place['name']}': {lat}")
    if lng is not None and not (-180 <= lng <= 180):
        raise ValueError(f"Longitud fuera de rango en '{place['name']}': {lng}")


# ---------------------------------------------------------------------------
# Lógica principal
# ---------------------------------------------------------------------------

def get_connection(db_path=DB_PATH):
    """
    Abre una conexión a la base de datos, creando la carpeta contenedora
    si no existe todavía.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(cursor):
    cursor.execute(SCHEMA)
    cursor.execute(INDEX_CATEGORY)


def seed_places(cursor, places, reset=False):
    """
    Inserta o actualiza los lugares. Si reset=True, borra los existentes
    antes de insertar (usar con cuidado, es destructivo).
    """
    for place in places:
        validate_place(place)

    if reset:
        logger.warning("Borrando todos los registros existentes de 'places'...")
        cursor.execute("DELETE FROM places")

    cursor.executemany(UPSERT_SQL, places)


def main():
    parser = argparse.ArgumentParser(description="Seed de la base de datos de Lumi.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra todos los lugares existentes antes de insertar los nuevos.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Ruta al archivo de base de datos (por defecto: database/lumi.db).",
    )
    args = parser.parse_args()

    try:
        with closing(get_connection(args.db_path)) as connection:
            with connection:  # commit automático al salir del bloque, rollback si hay error
                cursor = connection.cursor()
                create_schema(cursor)
                seed_places(cursor, PLACES, reset=args.reset)

        logger.info("✅ Datos insertados/actualizados correctamente (%d lugares).", len(PLACES))

    except sqlite3.Error as error:
        logger.error("❌ Error de base de datos: %s", error)
        raise
    except ValueError as error:
        logger.error("❌ Error de validación de datos: %s", error)
        raise


if __name__ == "__main__":
    main()