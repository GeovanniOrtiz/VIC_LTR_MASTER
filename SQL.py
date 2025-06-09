import mysql.connector as MySQLdb
from mysql.connector import Error
from PySide6.QtWidgets import QTableWidgetItem

class managerDataBase:
    def __init__(self, client):
        self.client = client
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'passwd': 'Airtemp',
            'db': 'LTR_Rack'
        }
        self.connection = None
        self.connect()

        self.db_piece = "LTR_Piece"
        self.db_master = "LTR_Master"
        self.db_backup = "backup"

        self.CreateTable(self.db_piece)
        self.CreateTableMaster(self.db_master)

        # verifica el cliente actual 1 para puebla y 2 para merida
        if self.client == 1:
            self.CreateTableData(self.db_backup)
        else:
            self.CreateTableData_Merida(self.db_backup)


    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = MySQLdb.connect(
                    host=self.db_config['host'],
                    user=self.db_config['user'],
                    passwd=self.db_config['passwd']
                )
                with self.connection.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['db']};")
                    cursor.execute(f"USE {self.db_config['db']};")
            except Error as e:
                print(f"Error connecting to database: {e}")
                self.connection = None
            else:
                print("Successfully connected to the database")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def reconnect_if_needed(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def execute_query(self, query, values=None):
        self.reconnect_if_needed()
        if self.connection:
            try:
                with self.connection.cursor(buffered=True) as cursor:
                    cursor.execute(query, values)
                    self.connection.commit()
                    return cursor
            except Error as e:
                print(f"Error executing query: {e}")
                # Ensure there are no unread results before reconnecting
                self.connection.reset_session()
                self.connect()
                return None
        return None

    def CreateTable(self, model):
        self.execute_query(
            f"CREATE TABLE IF NOT EXISTS {model} ("
            "id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "Nserie VARCHAR(40) NOT NULL, "
            "Code VARCHAR(60) NOT NULL, "
            "date DATETIME DEFAULT current_timestamp, "
            "f_etiqueta VARCHAR(30) NOT NULL, "
            "Cliente VARCHAR(20) NOT NULL);"
        )

    def CreateTableMaster(self, model):
        self.execute_query(
            f"CREATE TABLE IF NOT EXISTS {model} ("
            "id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "SerialMaster VARCHAR(40) NOT NULL, "
            "cantidadRack VARCHAR(40) NOT NULL, "
            "ordnt VARCHAR(40) NOT NULL, "
            "fcreate VARCHAR(40) NOT NULL, "
            "fproduction VARCHAR(40) NOT NULL, "
            "status VARCHAR(20) NOT NULL,"
            "Cliente VARCHAR(20) NOT NULL);"
        )

    def addMaster(self, Serial, cantidadRack, OT, fcreacion, fproduccion, status, Cliente):
        self.execute_query(
            f"INSERT INTO {self.db_master} (SerialMaster, cantidadRack, ordnt, fcreate, fproduction, status, Cliente) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (Serial, cantidadRack, OT, fcreacion, fproduccion, status, Cliente)
        )

    def addModule(self, nSerie, nCode, Fetiqueta, Cliente):
        self.execute_query(
            f"INSERT INTO {self.db_piece} (NSerie, Code, f_etiqueta, Cliente) VALUES (%s, %s, %s, %s)",
            (nSerie, nCode, Fetiqueta, Cliente)
        )

    def Check_nCode(self, nCode):
        cursor = self.execute_query(
            f"SELECT COUNT(*) FROM {self.db_piece} WHERE Code = %s",
            (nCode,)
        )
        if cursor:
            count = cursor.fetchone()[0]
            return count > 0
        return False

    def get_lastPartNo(self, serial):
        # Ejecuta la consulta SQL buscando el último registro con ese número de serie
        cursor = self.execute_query(
            f"SELECT * FROM {self.db_piece} WHERE Nserie = %s ORDER BY id DESC LIMIT 1",
            (serial,)
        )

        # Obtiene la primera fila del resultado (la más reciente)
        fila = cursor.fetchone()

        if fila:
            # Accede al valor en la posición 3 (índice 2) y separa por '-'
            partNo = fila[2]
            parte = partNo.split('-')[0]  # Toma solo la parte antes del guion
            return parte
        else:
            return None

    def InsertinTable(self, req, table, qty):
        print("Insertando datos en tabla")
        if req == 1:
            query = f"SELECT * FROM {self.db_piece} ORDER BY id DESC LIMIT {qty}"
        elif req == 2:
            query = f"SELECT * FROM {self.db_master} ORDER BY id DESC LIMIT {qty}"
        else:
            print("Solicitud no válida")
            return

        cursor = self.execute_query(query)
        if cursor:
            table.clearContents()
            table.setRowCount(0)
            index = 0

            for row in cursor.fetchall():
                table.setRowCount(index + 1)
                for col, value in enumerate(row):
                    table.setItem(index, col, QTableWidgetItem(str(value)))
                index += 1

            self.invertir_tabla(table)

    def invertir_tabla(self, tabla):
        row_count = tabla.rowCount()
        for i in range(row_count // 2):
            top_row = []
            bottom_row = []

            for column in range(tabla.columnCount()):
                item = tabla.takeItem(i, column)
                if item is not None:
                    top_row.append(item)

            for column in range(tabla.columnCount()):
                item = tabla.takeItem(row_count - 1 - i, column)
                if item is not None:
                    bottom_row.append(item)

            for column in range(tabla.columnCount()):
                if top_row:
                    tabla.setItem(row_count - 1 - i, column, top_row.pop(0))
                if bottom_row:
                    tabla.setItem(i, column, bottom_row.pop(0))

    def CreateTableData(self, table):
        self.execute_query(
            f"CREATE TABLE IF NOT EXISTS {table} ("
            "id INT UNSIGNED PRIMARY KEY, "
            "PartNo VARCHAR(40) NOT NULL, "
            "Supplier VARCHAR(40) NOT NULL, "
            "OT VARCHAR(40) NOT NULL, "
            "PzsTotales VARCHAR(40) NOT NULL, "
            "PzsRealizadas VARCHAR(40) NOT NULL, "
            "SerialNum VARCHAR(255) NOT NULL, "
            "FechaCreacion VARCHAR(255) NOT NULL,"
            "Cliente INT UNSIGNED NOT NULL);"
        )
        self.execute_query(
            f"INSERT IGNORE INTO {table} "
            "(id, PartNo, Supplier, OT, PzsTotales, PzsRealizadas, SerialNum, FechaCreacion, Cliente) "
            "VALUES (1, '5QM121251R', '43700413', '162555', '16', '0', '220425000000', '0', 0)"
        )

    def CreateTableData_Merida(self, table):
        self.execute_query(
            f"CREATE TABLE IF NOT EXISTS {table} ("
            "id INT UNSIGNED PRIMARY KEY, "
            "PartNo VARCHAR(40) NOT NULL, "
            "Supplier VARCHAR(40) NOT NULL, "
            "OT VARCHAR(40) NOT NULL, "
            "PzsTotales VARCHAR(40) NOT NULL, "
            "PzsRealizadas VARCHAR(40) NOT NULL, "
            "SerialNum VARCHAR(255) NOT NULL, "
            "FechaCreacion VARCHAR(255) NOT NULL,"
            "Cliente INT UNSIGNED NOT NULL);"
        )
        self.execute_query(
            f"INSERT IGNORE INTO {table} "
            "(id, PartNo, Supplier, OT, PzsTotales, PzsRealizadas, SerialNum, FechaCreacion, Cliente) "
            "VALUES (1, '5QM121251R', '6001003941', '162555', '16', '0', '1111220425000000', '0', 2)"
        )

    def updateData(self, PartNo, Supplier, OT, PzsTotales, PzsRealizadas, SerialNum, Fcreacion, Cliente):
        table = self.db_backup
        columnas = ["PartNo", "Supplier", "OT", "PzsTotales", "PzsRealizadas", "SerialNum", "FechaCreacion", "Cliente"]
        nuevos_valores = {
            "PartNo": PartNo,
            "Supplier": Supplier,
            "OT": OT,
            "PzsTotales": PzsTotales,
            "PzsRealizadas": PzsRealizadas,
            "SerialNum": SerialNum,
            "FechaCreacion": Fcreacion,
            "Cliente": Cliente
        }

        for columna in columnas:
            nuevo_valor = nuevos_valores[columna]
            self.execute_query(
                f"UPDATE {table} SET {columna} = %s",
                (nuevo_valor,)
            )

    def Get_Seial_Piece(self, serial_str, date_str, partNo):
        query = f"""
            SELECT * FROM {self.db_piece} 
            WHERE Code LIKE %s AND Code LIKE %s AND Code LIKE %s
            LIMIT 1
        """
        values = (f"%{serial_str}%", f"%{date_str}%", f"%{partNo}%")

        cursor = self.execute_query(query, values)

        if cursor:
            result = cursor.fetchone()
            if result:
                return list(result)
        return None
    def Get_Serial_Master_old(self, serial):
        cursor = self.execute_query(
            f"SELECT * FROM {self.db_piece} WHERE Nserie = %s",
            (serial,)
        )
        if cursor:
            result = cursor.fetchall()
            if result:
                return list(result)
        return None

    def Get_Serial_Master(self, serial):
        cursor = self.execute_query(
            f"SELECT * FROM {self.db_piece} WHERE Nserie = %s",
            (serial,)
        )
        if cursor:
            results = cursor.fetchall()
            if results:
                # Obtener solo la columna en la posición 2 (índice 1)
                datos = [fila[2] for fila in results]
                # Eliminar duplicados si los hubiera
                #datos_unicos = list(set(datos))
                return datos
        return None
    def GetDataBackUp(self):
        cursor = self.execute_query(
            f"SELECT * FROM {self.db_backup} WHERE id = %s",
            (1,)
        )
        if cursor:
            result = cursor.fetchone()
            if result:
                return list(result)
        return None

    def GetDataMaster(self, serial):
        cursor = self.execute_query(
            f"SELECT * FROM {self.db_master} WHERE SerialMaster = %s",
            (serial,)
        )
        if cursor:
            result = cursor.fetchone()
            if result:
                return list(result)
        return None

    def GetSerialMaster(self, tabla):
        cursor = self.execute_query(
            f"SELECT SerialMaster FROM {tabla}"
        )
        if cursor:
            return [registro[0] for registro in cursor.fetchall()]
        return []

    def GetOTMaster(self, tabla):
        cursor = self.execute_query(
            f"SELECT ordnt FROM {tabla}"
        )
        if cursor:
            try:
                resultados_set = set(registro[0] for registro in cursor.fetchall())
                return list(resultados_set)
            except Exception as e:
                print(f"Error al ejecutar la consulta: {e}")
        return []

    def _delete_last_registers(self, table, n):
        """
            Elimina los últimos 'n' registros insertados en la tabla especificada.

            :param nombre_tabla: Nombre de la tabla de la cual se eliminarán los registros.
            :param n: Número de registros a eliminar.
            """
        # Verificar que 'n' sea un entero positivo
        if not isinstance(n, int) or n <= 0:
            print("El número de registros a eliminar debe ser un entero positivo.")
            return

        # Consulta para obtener el número total de registros en la tabla
        consulta_contar = f"SELECT COUNT(*) FROM {table}"
        cursor = self.execute_query(consulta_contar)
        total_registros = cursor.fetchone()[0]

        if total_registros == 0:
            print("La tabla está vacía. No hay registros para eliminar.")
            return

        # Determinar cuántos registros eliminar realmente
        registros_a_eliminar = min(n, total_registros)

        # Consulta para eliminar los últimos 'registros_a_eliminar' registros
        consulta_delete = f"""
                DELETE FROM {table}
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id FROM {table}
                        ORDER BY id DESC
                        LIMIT {registros_a_eliminar}
                    ) AS subconsulta
                )
            """
        cursor = self.execute_query(consulta_delete)
        if cursor:
            print(f"Se eliminaron {cursor.rowcount} registros.")
        else:
            print("No se pudieron eliminar los registros.")

    def _delete_last_rows(self, table, n):
        """
        Elimina las últimas 'n' filas de un QTableWidget.

        :param table: El QTableWidget del cual se eliminarán las filas.
        :param n: Número de filas a eliminar desde el final de la tabla.
        """
        total_filas = table.rowCount()
        if n > total_filas:
            n = total_filas  # Si 'n' es mayor que el total de filas, ajustamos 'n' al total disponible

        for i in range(n):
            table.removeRow(total_filas - 1 - i)