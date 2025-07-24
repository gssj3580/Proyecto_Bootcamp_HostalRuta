import mysql.connector

# --- CONFIGURACIÓN DE TU BASE DE DATOS MySQL ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario_mysql',  # ¡CAMBIA ESTO!
    'password': 'tu_contraseña_mysql', # ¡CAMBIA ESTO!
    'database': 'hotel_db_hackathon' # Nombre de la BD que crearemos
}

def setup_database():
    try:
        # Conectar al servidor MySQL sin especificar una BD inicial
        cnx = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = cnx.cursor()

        # Crear la base de datos si no existe
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            print(f"Base de datos '{DB_CONFIG['database']}' verificada/creada.")
        except mysql.connector.Error as err:
            print(f"Error al crear la base de datos: {err}")
            cursor.close()
            cnx.close()
            return False

        # Conectar a la base de datos recién creada o existente
        cnx.database = DB_CONFIG['database']
        cursor = cnx.cursor() # Obtener un nuevo cursor para la nueva BD

        # Crear la tabla de habitaciones
        create_table_query = """
        CREATE TABLE IF NOT EXISTS rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_number VARCHAR(10) UNIQUE NOT NULL,
            room_type VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            last_cleaned_date DATE
        );
        """
        cursor.execute(create_table_query)
        print("Tabla 'rooms' verificada/creada.")

        # Insertar algunos datos iniciales si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM rooms;")
        if cursor.fetchone()[0] == 0:
            initial_data = [
                ('101', 'Standard', 100.00, True, '2025-07-23'),
                ('102', 'Standard', 100.00, True, '2025-07-23'),
                ('201', 'Deluxe', 150.00, True, '2025-07-23'),
                ('202', 'Deluxe', 150.00, True, '2025-07-23'),
                ('301', 'Suite', 250.00, True, '2025-07-23'),
                ('302', 'Standard', 100.00, False, '2025-07-23'), # Ejemplo de habitación no disponible
            ]
            insert_query = """
            INSERT INTO rooms (room_number, room_type, price, is_available, last_cleaned_date)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.executemany(insert_query, initial_data)
            cnx.commit()
            print("Datos iniciales insertados en la tabla 'rooms'.")
        else:
            print("La tabla 'rooms' ya contiene datos.")

        print("Configuración de la base de datos completada.")
        return True

    except mysql.connector.Error as err:
        print(f"Error general de MySQL: {err}")
        return False
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

if __name__ == '__main__':
    if setup_database():
        print("Preparación de la base de datos exitosa.")
    else:
        print("Fallo en la preparación de la base de datos.")