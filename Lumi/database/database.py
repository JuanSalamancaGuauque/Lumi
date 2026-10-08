import sqlite3
from pathlib import Path


# Ruta ABSOLUTA a lumi.db, calculada a partir de la ubicacion de ESTE
# archivo (database/database.py). Asi no depende de desde que carpeta
# se ejecute la app.
#
# Antes era "database/lumi.db" (ruta relativa): solo funcionaba si
# el comando se ejecutaba desde la carpeta Lumi/Lumi. Si se ejecutaba
# desde otra carpeta (por ejemplo, el boton "Run" de VS Code abriendo
# la carpeta de arriba), SQLite no encontraba la carpeta "database/"
# y fallaba con "unable to open database file".
DB_PATH = Path(__file__).resolve().parent / "lumi.db"


class Database:

    def __init__(self):

        self.db_path = str(DB_PATH)

    def connect(self):

        connection = sqlite3.connect(self.db_path)

        # Permite acceder a las columnas por nombre
        connection.row_factory = sqlite3.Row

        return connection