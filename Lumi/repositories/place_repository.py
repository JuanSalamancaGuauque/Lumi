from database.database import Database
import random

class PlaceRepository:

    def __init__(self):
        self.database = Database()

    def get_all(self):

        connection = self.database.connect()

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM places")

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]


    def get_by_category(self, category):

        connection = self.database.connect()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM places WHERE category = ?",
            (category,)
        )

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]


    def get_by_name(self, name):

        connection = self.database.connect()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM places WHERE name = ?",
            (name,)
        )

        row = cursor.fetchone()

        connection.close()

        if row:
            return dict(row)

        return None

    def get_random(self):

        places = self.get_all()

        if not places:
            return None

        return random.choice(places)