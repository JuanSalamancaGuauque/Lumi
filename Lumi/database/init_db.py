"""
Script de inicializacion / seed de la base de datos de Lumi.

MODELO FASE 1: reemplaza la tabla plana "places" por un modelo
normalizado: zona, categoria, lugar, lugar_categoria (tabla puente
para la relacion muchos-a-muchos) e imagen. Tambien agrega el
catalogo estado_avatar para la mascota (YA con los 5 archivos
reales entregados por el equipo de animacion: saludo, pensando,
hablando, feliz y error).

FASE 3 (zona piloto): se agrega la zona "Chapinero" con 7 lugares
reales (verificados via busqueda web y Google Places), 5 categorias
nuevas (iglesia, libreria, gastronomia, restaurante, sendero) y sus
relaciones. Ninguno de estos 7 lugares tiene fotos todavia, por eso
no aparecen en la lista de "imagenes" (se agregan despues).

Es seguro ejecutarlo varias veces: usa UPSERT por nombre, asi no
duplica datos ni recicla IDs innecesariamente.

Uso:
    python init_db.py            # crea/actualiza el esquema y los datos
    python init_db.py --reset    # borra los datos de estas tablas y los vuelve a insertar
"""

import argparse
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

# CORREGIDO: la version anterior tenia un bug aqui. Este archivo YA vive
# dentro de la carpeta "database/", asi que agregar "database/" de nuevo
# apuntaba a "database/database/lumi.db" (una ruta que nunca existio).
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lumi.db"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Datos base
# ---------------------------------------------------------------------------

ZONAS = [
    {
        "nombre": "Centro historico (Santa Fe / La Candelaria)",
        "descripcion": "Corazon historico, cultural y patrimonial de Bogota.",
        "ciudad": "Bogota",
    },
    {
        "nombre": "Engativa",
        "descripcion": "Localidad del noroccidente de Bogota.",
        "ciudad": "Bogota",
    },
    {
        "nombre": "Chapinero",
        "descripcion": (
            "Zona piloto del proyecto Lumi: mezcla de gastronomia, "
            "cultura, comercio y naturaleza al oriente de Bogota."
        ),
        "ciudad": "Bogota",
    },
]

CATEGORIAS = [
    {"nombre": "mirador", "descripcion": "Puntos con vistas panoramicas de la ciudad."},
    {"nombre": "museo", "descripcion": "Espacios culturales y de exhibicion."},
    {"nombre": "parque", "descripcion": "Espacios verdes y naturales."},
    {"nombre": "iglesia", "descripcion": "Templos y sitios de arquitectura religiosa."},
    {"nombre": "libreria", "descripcion": "Librerias y espacios de lectura."},
    {"nombre": "gastronomia", "descripcion": "Distritos y experiencias gastronomicas."},
    {"nombre": "restaurante", "descripcion": "Restaurantes recomendados."},
    {"nombre": "sendero", "descripcion": "Senderos ecologicos y rutas de caminata."},
]

# Cada lugar referencia su zona y categorias por NOMBRE (no por id), para
# que el script resuelva las referencias sin depender de ids fijos.
LUGARES = [
    {
        "nombre": "Monserrate",
        "zona": "Centro historico (Santa Fe / La Candelaria)",
        "categorias": ["mirador"],
        "descripcion": "Uno de los lugares turisticos mas visitados de Bogota.",
        "horario_texto": "Lunes a Domingo 5:00 AM - 10:00 PM",
        "latitud": 4.6057,
        "longitud": -74.0566,
        "imagenes": [
            {
                "archivo": "monserrate.jpg",
                "texto_alternativo": (
                    "Vista del cerro de Monserrate con la iglesia en la "
                    "cima, rodeada de vegetacion y nubes bajas."
                ),
                "es_principal": 1,
            }
        ],
    },
    {
        "nombre": "Museo del Oro",
        "zona": "Centro historico (Santa Fe / La Candelaria)",
        "categorias": ["museo"],
        "descripcion": (
            "Museo con una de las colecciones de oro prehispanico mas "
            "importantes del mundo."
        ),
        "horario_texto": "Martes a Domingo 9:00 AM - 5:00 PM",
        "latitud": 4.6019,
        "longitud": -74.0723,
        "imagenes": [
            {
                # NOTA: este archivo todavia no existe en static/images/.
                # Hay que conseguirlo/subirlo.
                "archivo": "museo_oro.jpg",
                "texto_alternativo": "Fachada del Museo del Oro en el centro de Bogota.",
                "es_principal": 1,
            }
        ],
    },
    {
        "nombre": "Jardin Botanico",
        "zona": "Engativa",
        "categorias": ["parque"],
        "descripcion": "Espacio natural con una gran diversidad de flora colombiana.",
        "horario_texto": "8:00 AM - 5:00 PM",
        "latitud": 4.6676,
        "longitud": -74.1048,
        "imagenes": [
            {
                # NOTA: este archivo todavia no existe en static/images/.
                # Hay que conseguirlo/subirlo.
                "archivo": "jardin_botanico.jpg",
                "texto_alternativo": "Senderos y vegetacion del Jardin Botanico de Bogota.",
                "es_principal": 1,
            }
        ],
    },

    # -----------------------------------------------------------------
    # FASE 3 - Zona piloto Chapinero (7 lugares, datos verificados)
    # Ninguno tiene foto real todavia: no se incluye "imagenes".
    # -----------------------------------------------------------------

    {
        "nombre": "Basilica Menor Nuestra Senora de Lourdes",
        "zona": "Chapinero",
        "categorias": ["iglesia"],
        "descripcion": (
            "Templo de estilo neogotico construido en 1875, el segundo "
            "mas alto de Bogota con mas de 60 metros. Fue elevado a "
            "basilica menor y se destaca por sus vitrales y su fachada "
            "en piedra, considerada el simbolo arquitectonico de Chapinero."
        ),
        "horario_texto": (
            "Lunes a Viernes 7:00 AM - 6:30 PM, "
            "Sabado 7:30 AM - 6:30 PM, "
            "Domingo 6:30 AM - 7:00 PM"
        ),
        "latitud": 4.6495531,
        "longitud": -74.0623099,
    },
    {
        "nombre": "Libreria Wilborada 1047",
        "zona": "Chapinero",
        "categorias": ["libreria"],
        "descripcion": (
            "Libreria y cafe dentro de una casa patrimonial de 1943, de "
            "estilo ingles, en el barrio Quinta Camacho. Tiene patios "
            "internos y una agenda cultural con tertulias y lecturas "
            "infantiles. Su nombre rinde homenaje a Wilborada, patrona "
            "de los libreros."
        ),
        "horario_texto": "Lunes a Sabado 10:00 AM - 7:00 PM, Domingo 12:00 PM - 4:00 PM",
        "latitud": 4.6558210,
        "longitud": -74.0589199,
    },
    {
        "nombre": "Zona G",
        "zona": "Chapinero",
        "categorias": ["gastronomia"],
        "descripcion": (
            "Distrito gastronomico de Chapinero (la 'G' es de 'Gourmet'), "
            "ubicado entre las calles 65 y 71. Reune restaurantes de "
            "chefs colombianos reconocidos, con cocina internacional y "
            "colombiana de alta gama."
        ),
        "horario_texto": "Varia segun el restaurante, en general de 12:00 PM a 11:00 PM",
        "latitud": 4.6468856,
        "longitud": -74.0559631,
    },
    {
        "nombre": "Mesa Franca",
        "zona": "Chapinero",
        "categorias": ["restaurante"],
        "descripcion": (
            "Restaurante en Chapinero Alto conocido por su cocina "
            "colombiana contemporanea con enfoque en ingredientes "
            "locales. Muy bien valorado por su propuesta creativa."
        ),
        "horario_texto": (
            "Martes 7:00 PM - 10:00 PM, "
            "Miercoles a Jueves 12:00 PM - 4:00 PM y 7:00 PM - 10:00 PM, "
            "Viernes 12:00 PM - 4:00 PM y 7:00 PM - 11:00 PM, "
            "Sabado 1:00 PM - 11:00 PM, "
            "Domingo 1:00 PM - 5:00 PM, "
            "Lunes cerrado"
        ),
        "latitud": 4.6461291,
        "longitud": -74.0601291,
    },
    {
        "nombre": "Parque El Virrey",
        "zona": "Chapinero",
        "categorias": ["parque"],
        "descripcion": (
            "Parque lineal de 10 hectareas con un riachuelo, senderos "
            "peatonales y ciclorruta. Ideal para trotar, hacer picnic o "
            "pasear con mascotas, rodeado de cafes y restaurantes."
        ),
        "horario_texto": "Abierto las 24 horas",
        "latitud": 4.6732479,
        "longitud": -74.0540574,
    },
    {
        "nombre": "Parque de la 93",
        "zona": "Chapinero",
        "categorias": ["parque"],
        "descripcion": (
            "Plaza publica rodeada de restaurantes y cafes con terraza, "
            "sede frecuente de eventos culturales y actividades de "
            "temporada. Cuenta con zona infantil y espacio para mascotas."
        ),
        "horario_texto": "Abierto las 24 horas",
        "latitud": 4.6765317,
        "longitud": -74.0484162,
    },
    {
        "nombre": "Quebrada La Vieja",
        "zona": "Chapinero",
        "categorias": ["sendero"],
        "descripcion": (
            "Sendero ecologico dentro de la Reserva Forestal Protectora "
            "de los Cerros Orientales, ideal para caminatas y "
            "avistamiento de aves, con vistas panoramicas de Bogota. "
            "Requiere reserva previa GRATUITA a traves de la pagina "
            "'Caminos de los Cerros Orientales' (caminos.eaab.gov.co), "
            "con confirmacion por codigo QR antes de ingresar."
        ),
        "horario_texto": (
            "Lunes a Viernes 6:00 AM - 3:00 PM, "
            "Sabado y Domingo 6:00 AM - 11:00 AM "
            "(requiere reserva previa, ver descripcion)"
        ),
        "latitud": 4.6501285,
        "longitud": -74.0485573,
    },
]

# YA REAL: el equipo de animacion entrego estos 5 GIFs (en
# static/images/). Ojo, cambiaron respecto al plan original:
# no llego "despedida", pero si llegaron "feliz" y "error".
# El frontend los usa en frontend/js/avatar.js (AVATAR_STATES).
ESTADOS_AVATAR = [
    {
        "nombre_estado": "saludo",
        "archivo_gif": "SALUDO LUMI.gif",
        "descripcion": "Se activa al iniciar la conversacion o saludar.",
    },
    {
        "nombre_estado": "pensando",
        "archivo_gif": "PENSANDO LUMI.gif",
        "descripcion": "Se activa mientras se consulta a Gemini.",
    },
    {
        "nombre_estado": "hablando",
        "archivo_gif": "HABLANDO LUMI.gif",
        "descripcion": "Se activa mientras Lumi esta respondiendo por voz.",
    },
    {
        "nombre_estado": "feliz",
        "archivo_gif": "FELIZ LUMI.gif",
        "descripcion": "Estado de reposo, despues de responder.",
    },
    {
        "nombre_estado": "idle",
        "archivo_gif": "IDLE LUMI.gif",
        "descripcion": "Reposo general, cuando no hay actividad en la conversacion.",
    },
    {
        "nombre_estado": "error",
        "archivo_gif": "ERROR LUMI.gif",
        "descripcion": "Se activa cuando falla la conexion o la IA.",
    },
]


# ---------------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS zona (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL UNIQUE,
    descripcion   TEXT,
    ciudad        TEXT NOT NULL DEFAULT 'Bogota'
);

CREATE TABLE IF NOT EXISTS categoria (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL UNIQUE,
    descripcion   TEXT
);

CREATE TABLE IF NOT EXISTS lugar (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id         INTEGER NOT NULL,
    nombre          TEXT NOT NULL UNIQUE,
    descripcion     TEXT NOT NULL,
    latitud         REAL CHECK (latitud BETWEEN -90 AND 90),
    longitud        REAL CHECK (longitud BETWEEN -180 AND 180),
    horario_texto   TEXT NOT NULL,
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    creado_en       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (zona_id) REFERENCES zona(id)
);

CREATE INDEX IF NOT EXISTS idx_lugar_zona ON lugar(zona_id);

CREATE TABLE IF NOT EXISTS lugar_categoria (
    lugar_id      INTEGER NOT NULL,
    categoria_id  INTEGER NOT NULL,
    PRIMARY KEY (lugar_id, categoria_id),
    FOREIGN KEY (lugar_id)     REFERENCES lugar(id)     ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lugar_categoria_categoria ON lugar_categoria(categoria_id);

CREATE TABLE IF NOT EXISTS imagen (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    lugar_id           INTEGER NOT NULL,
    archivo            TEXT NOT NULL,
    texto_alternativo  TEXT NOT NULL,
    orden              INTEGER NOT NULL DEFAULT 0,
    es_principal       INTEGER NOT NULL DEFAULT 0 CHECK (es_principal IN (0, 1)),
    FOREIGN KEY (lugar_id) REFERENCES lugar(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_imagen_lugar ON imagen(lugar_id);

CREATE TABLE IF NOT EXISTS estado_avatar (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_estado  TEXT NOT NULL UNIQUE,
    archivo_gif    TEXT NOT NULL,
    descripcion    TEXT
);
"""


# ---------------------------------------------------------------------------
# Logica principal
# ---------------------------------------------------------------------------

def get_connection(db_path=DB_PATH):
    """
    Abre una conexion a la base de datos, creando la carpeta contenedora
    si no existe todavia.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(cursor):
    cursor.executescript(SCHEMA)


def drop_legacy_places_table(cursor):
    """
    La tabla "places" (modelo plano de la version anterior) queda
    reemplazada por el modelo normalizado. Sus 3 registros ya fueron
    migrados a mano dentro de LUGARES, asi que es seguro eliminarla.
    """
    cursor.execute("DROP TABLE IF EXISTS places")


def get_id_by_name(cursor, table, nombre):
    cursor.execute(f"SELECT id FROM {table} WHERE nombre = ?", (nombre,))
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"No se encontro '{nombre}' en la tabla '{table}'.")
    return row[0]


def upsert_zonas(cursor, zonas):
    for zona in zonas:
        cursor.execute(
            """
            INSERT INTO zona (nombre, descripcion, ciudad)
            VALUES (:nombre, :descripcion, :ciudad)
            ON CONFLICT(nombre) DO UPDATE SET
                descripcion = excluded.descripcion,
                ciudad = excluded.ciudad
            """,
            zona,
        )


def upsert_categorias(cursor, categorias):
    for categoria in categorias:
        cursor.execute(
            """
            INSERT INTO categoria (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            ON CONFLICT(nombre) DO UPDATE SET
                descripcion = excluded.descripcion
            """,
            categoria,
        )


def upsert_lugares(cursor, lugares):
    for lugar in lugares:
        zona_id = get_id_by_name(cursor, "zona", lugar["zona"])

        cursor.execute(
            """
            INSERT INTO lugar (zona_id, nombre, descripcion, latitud, longitud, horario_texto)
            VALUES (:zona_id, :nombre, :descripcion, :latitud, :longitud, :horario_texto)
            ON CONFLICT(nombre) DO UPDATE SET
                zona_id = excluded.zona_id,
                descripcion = excluded.descripcion,
                latitud = excluded.latitud,
                longitud = excluded.longitud,
                horario_texto = excluded.horario_texto,
                actualizado_en = CURRENT_TIMESTAMP
            """,
            {
                "zona_id": zona_id,
                "nombre": lugar["nombre"],
                "descripcion": lugar["descripcion"],
                "latitud": lugar["latitud"],
                "longitud": lugar["longitud"],
                "horario_texto": lugar["horario_texto"],
            },
        )

        lugar_id = get_id_by_name(cursor, "lugar", lugar["nombre"])

        # Relacion con categorias (tabla puente muchos-a-muchos)
        for nombre_categoria in lugar["categorias"]:
            categoria_id = get_id_by_name(cursor, "categoria", nombre_categoria)
            cursor.execute(
                "INSERT OR IGNORE INTO lugar_categoria (lugar_id, categoria_id) VALUES (?, ?)",
                (lugar_id, categoria_id),
            )

        # Imagenes: se borran y se vuelven a insertar para este lugar,
        # asi el re-seed no va acumulando duplicados en cada corrida.
        cursor.execute("DELETE FROM imagen WHERE lugar_id = ?", (lugar_id,))
        for orden, imagen in enumerate(lugar.get("imagenes", []), start=1):
            cursor.execute(
                """
                INSERT INTO imagen (lugar_id, archivo, texto_alternativo, orden, es_principal)
                VALUES (:lugar_id, :archivo, :texto_alternativo, :orden, :es_principal)
                """,
                {
                    "lugar_id": lugar_id,
                    "archivo": imagen["archivo"],
                    "texto_alternativo": imagen["texto_alternativo"],
                    "orden": orden,
                    "es_principal": imagen.get("es_principal", 0),
                },
            )


def upsert_estados_avatar(cursor, estados):
    for estado in estados:
        cursor.execute(
            """
            INSERT INTO estado_avatar (nombre_estado, archivo_gif, descripcion)
            VALUES (:nombre_estado, :archivo_gif, :descripcion)
            ON CONFLICT(nombre_estado) DO UPDATE SET
                archivo_gif = excluded.archivo_gif,
                descripcion = excluded.descripcion
            """,
            estado,
        )


def reset_data(cursor):
    """Borra los datos (no el esquema) de las tablas nuevas. Uso: --reset."""
    logger.warning("Borrando datos existentes de zona/categoria/lugar/imagen/estado_avatar...")
    # El orden importa por las llaves foraneas: primero las tablas "hijas".
    cursor.execute("DELETE FROM imagen")
    cursor.execute("DELETE FROM lugar_categoria")
    cursor.execute("DELETE FROM lugar")
    cursor.execute("DELETE FROM categoria")
    cursor.execute("DELETE FROM zona")
    cursor.execute("DELETE FROM estado_avatar")


def main():
    parser = argparse.ArgumentParser(description="Seed de la base de datos de Lumi (modelo Fase 1).")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra los datos existentes de las tablas nuevas antes de insertar los nuevos.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Ruta al archivo de base de datos (por defecto: lumi.db en esta misma carpeta).",
    )
    args = parser.parse_args()

    try:
        with closing(get_connection(args.db_path)) as connection:
            with connection:  # commit automatico al salir, rollback si hay error
                cursor = connection.cursor()
                create_schema(cursor)
                drop_legacy_places_table(cursor)

                if args.reset:
                    reset_data(cursor)

                upsert_zonas(cursor, ZONAS)
                upsert_categorias(cursor, CATEGORIAS)
                upsert_lugares(cursor, LUGARES)
                upsert_estados_avatar(cursor, ESTADOS_AVATAR)

        logger.info(
            "Esquema y datos actualizados: %d zonas, %d categorias, %d lugares, %d estados de avatar.",
            len(ZONAS), len(CATEGORIAS), len(LUGARES), len(ESTADOS_AVATAR),
        )

    except sqlite3.Error as error:
        logger.error("Error de base de datos: %s", error)
        raise
    except ValueError as error:
        logger.error("Error de referencia de datos: %s", error)
        raise


if __name__ == "__main__":
    main()