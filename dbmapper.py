from sqlite3 import DatabaseError
from applib import Nomenclature

class NomenclatureMapper:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def find_by_id(self, id_nomenclature):
        sql_statement = f"SELECT ID, NAME, DESCRIPTION \
            FROM NOMENCLATURE WHERE ID='{id_nomenclature}'"
        self.cursor.execute(sql_statement)
        result = self.cursor.fetchone()
        if result:
            return Nomenclature(*result)
        else:
            return None

    def insert(self, nomenclature):
        sql_statement = f"INSERT INTO NOMENCLATURE (NAME, DESCRIPTION) VALUES \
            ('{nomenclature.name}', '{nomenclature.description}')"
        self.cursor.execute(sql_statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DatabaseError(e.args)

    def update(self, nomenclature):
        sql_statement = f"UPDATE NOMENCLATURE SET NAME='{nomenclature.name}', \
            DESCRIPTION='{nomenclature.description}' \
            WHERE ID='{nomenclature.id}'"
        self.cursor.execute(sql_statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DatabaseError(e.args)

    def delete(self, nomenclature):
        sql_statement = f"DELETE FROM NOMENCLATURE WHERE ID='{nomenclature.id}'"
        self.cursor.execute(sql_statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DatabaseError(e.args)

    def fetchall(self):
        sql_statement = f"SELECT ID, NAME, DESCRIPTION FROM NOMENCLATURE"
        self.cursor.execute(sql_statement)
        entries = self.cursor.fetchall()
        result = []
        if entries:
            for entry in entries:
                result.append(Nomenclature(*entry))
        return result