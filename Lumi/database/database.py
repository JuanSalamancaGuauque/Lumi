import sqlite3


class Database:

    def __init__(self):

        self.db_path = "database/lumi.db"

    def connect(self):

        connection = sqlite3.connect(self.db_path)

        # Permite acceder a las columnas por nombre
        connection.row_factory = sqlite3.Row

        return connection