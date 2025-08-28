import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",       # o la IP de tu servidor MySQL
            user="root",            # tu usuario de MySQL
            password="NAviSEyer10", # tu contraseña
            database="control_actividades"
        )
        return connection
    except Error as e:
        print("Error de conexión a MySQL:", e)
        return None