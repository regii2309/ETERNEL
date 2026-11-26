
import sqlite3
import os

CARPETA = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(CARPETA, "database.db")


def crear_base_datos():
    conexion = sqlite3.connect(DATABASE)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        )
    """)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            zona TEXT NOT NULL,
            mesa_numero INTEGER NOT NULL,
            capacidad INTEGER NOT NULL,
            personas INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'confirmada',
            creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    conexion.commit()
    conexion.close()

    print("Base de datos de ETERNEL preparada correctamente.")


if __name__ == "__main__":
    crear_base_datos()
