import random

from database.database import Database


class PlaceRepository:
    """
    Repositorio de lugares, adaptado al modelo normalizado (Fase 1):
    lugar + zona + categoria (N:M vía lugar_categoria) + imagen.

    Cada método sigue devolviendo diccionarios "planos" con toda la
    información ya armada (zona, categorías, imágenes), para que el resto
    del código (nlp.py, assistant_service.py) no tenga que preocuparse
    por hacer los JOINs por su cuenta.

    OJO: los nombres de los campos cambiaron respecto a la versión
    anterior (inglés -> español, siguiendo el nuevo esquema):
        "name"      -> "nombre"
        "category"  -> "categorias" (ahora es una LISTA, puede haber más de una)
        "description" -> "descripcion"
        "schedule"  -> "horario_texto"
        "latitude"  -> "latitud"
        "longitude" -> "longitud"
        "image"     -> "imagen_principal" (más "imagenes", la lista completa)
    """

    def __init__(self):
        self.database = Database()

    # -----------------------------------------------------------------
    # Armado de cada lugar (categorías + imágenes)
    # -----------------------------------------------------------------

    def _attach_categorias_e_imagenes(self, connection, place):
        """
        Un JOIN directo entre lugar, categoria e imagen duplicaría la fila
        del lugar por cada combinación posible (ej. 2 categorías x 3
        imágenes = 6 filas para el mismo lugar). Por eso se resuelve con
        dos consultas adicionales, más simples de leer y sin duplicados.
        """
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT c.nombre
            FROM categoria c
            JOIN lugar_categoria lc ON lc.categoria_id = c.id
            WHERE lc.lugar_id = ?
            """,
            (place["id"],),
        )
        place["categorias"] = [row["nombre"] for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT archivo, texto_alternativo, orden, es_principal
            FROM imagen
            WHERE lugar_id = ?
            ORDER BY es_principal DESC, orden ASC
            """,
            (place["id"],),
        )
        place["imagenes"] = [dict(row) for row in cursor.fetchall()]
        place["imagen_principal"] = (
            place["imagenes"][0]["archivo"] if place["imagenes"] else None
        )

        return place

    _LUGAR_CON_ZONA_SQL = """
        SELECT
            lugar.id,
            lugar.nombre,
            lugar.descripcion,
            lugar.latitud,
            lugar.longitud,
            lugar.horario_texto,
            lugar.activo,
            zona.nombre AS zona_nombre,
            zona.ciudad AS ciudad
        FROM lugar
        JOIN zona ON zona.id = lugar.zona_id
    """

    # -----------------------------------------------------------------
    # Consultas públicas
    # -----------------------------------------------------------------

    def get_all(self):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(f"{self._LUGAR_CON_ZONA_SQL} WHERE lugar.activo = 1")
        rows = cursor.fetchall()

        places = [
            self._attach_categorias_e_imagenes(connection, dict(row))
            for row in rows
        ]

        connection.close()
        return places

    def get_by_category(self, category_name):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(
            f"""
            {self._LUGAR_CON_ZONA_SQL}
            JOIN lugar_categoria lc ON lc.lugar_id = lugar.id
            JOIN categoria c ON c.id = lc.categoria_id
            WHERE c.nombre = ? AND lugar.activo = 1
            """,
            (category_name,),
        )
        rows = cursor.fetchall()

        places = [
            self._attach_categorias_e_imagenes(connection, dict(row))
            for row in rows
        ]

        connection.close()
        return places

    def get_by_name(self, name):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(
            f"{self._LUGAR_CON_ZONA_SQL} WHERE lugar.nombre = ? AND lugar.activo = 1",
            (name,),
        )
        row = cursor.fetchone()

        place = (
            self._attach_categorias_e_imagenes(connection, dict(row))
            if row
            else None
        )

        connection.close()
        return place

    def get_by_zona(self, zona_name):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(
            f"{self._LUGAR_CON_ZONA_SQL} WHERE zona.nombre = ? AND lugar.activo = 1",
            (zona_name,),
        )
        rows = cursor.fetchall()

        places = [
            self._attach_categorias_e_imagenes(connection, dict(row))
            for row in rows
        ]

        connection.close()
        return places

    def get_random(self):
        places = self.get_all()

        if not places:
            return None

        return random.choice(places)