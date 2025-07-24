from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import pandas as pd
import numpy as np
from datetime import date, timedelta

# --- CONFIGURACIÓN DE TU BASE DE DATOS MySQL (DEBE SER LA MISMA QUE database_setup.py) ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario_mysql',  # ¡CAMBIA ESTO!
    'password': 'tu_contraseña_mysql', # ¡CAMBIA ESTO!
    'database': 'hotel_db_hackathon'
}

app = Flask(__name__)
app.secret_key = 'supersecretkey_hackathon' # Clave secreta para flashear mensajes

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        flash('Error al conectar con la base de datos.', 'error')
        return None

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        return render_template('index.html', rooms=[]) # Renderiza la plantilla sin datos si hay error
    cursor = conn.cursor(dictionary=True) # dictionary=True para obtener resultados como diccionarios
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', rooms=rooms)

@app.route('/add', methods=('GET', 'POST'))
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']
        is_available = 'is_available' in request.form
        last_cleaned_date = request.form['last_cleaned_date']

        if not room_number or not room_type or not price:
            flash('Todos los campos obligatorios deben ser completados!', 'error')
        else:
            conn = get_db_connection()
            if conn is None:
                return redirect(url_for('add_room'))
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO rooms (room_number, room_type, price, is_available, last_cleaned_date) VALUES (%s, %s, %s, %s, %s)",
                    (room_number, room_type, price, is_available, last_cleaned_date)
                )
                conn.commit()
                flash('Habitación añadida exitosamente!', 'success')
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                if "Duplicate entry" in str(err) and "for key 'rooms.room_number'" in str(err):
                    flash(f'Error: El número de habitación "{room_number}" ya existe.', 'error')
                else:
                    flash(f'Error al añadir habitación: {err}', 'error')
            finally:
                cursor.close()
                conn.close()
    return render_template('add_room.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_room(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE id = %s", (id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()

    if room is None:
        flash('Habitación no encontrada.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']
        is_available = 'is_available' in request.form
        last_cleaned_date = request.form['last_cleaned_date']

        if not room_number or not room_type or not price:
            flash('Todos los campos obligatorios deben ser completados!', 'error')
        else:
            conn = get_db_connection()
            if conn is None:
                return redirect(url_for('edit_room', id=id))
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE rooms SET room_number = %s, room_type = %s, price = %s, is_available = %s, last_cleaned_date = %s WHERE id = %s",
                    (room_number, room_type, price, is_available, last_cleaned_date, id)
                )
                conn.commit()
                flash('Habitación actualizada exitosamente!', 'success')
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                if "Duplicate entry" in str(err) and "for key 'rooms.room_number'" in str(err):
                    flash(f'Error: El número de habitación "{room_number}" ya existe.', 'error')
                else:
                    flash(f'Error al actualizar habitación: {err}', 'error')
            finally:
                cursor.close()
                conn.close()
    return render_template('edit_room.html', room=room)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_room(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM rooms WHERE id = %s", (id,))
        conn.commit()
        flash('Habitación eliminada exitosamente!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error al eliminar habitación: {err}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

# --- Análisis de Datos Exploratorio ---
@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    if conn is None:
        return render_template('analytics.html', stats={})
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT room_type, COUNT(*) as total_rooms, SUM(is_available) as available_rooms FROM rooms GROUP BY room_type")
    room_data = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(room_data)

    if not df.empty:
        df['occupied_rooms'] = df['total_rooms'] - df['available_rooms']
        df['occupancy_rate'] = (df['occupied_rooms'] / df['total_rooms'] * 100).round(2)
        # Convertir a formato que sea fácil de pasar a la plantilla
        stats = df.to_dict(orient='records')
    else:
        stats = []

    # Ejemplo de datos históricos simulados para una "tendencia"
    # Esto es puramente demostrativo para la Hackathon
    historical_occupancy = {
        (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'): 0.70,
        (date.today() - timedelta(days=6)).strftime('%Y-%m-%d'): 0.75,
        (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'): 0.80,
        (date.today() - timedelta(days=4)).strftime('%Y-%m-%d'): 0.82,
        (date.today() - timedelta(days=3)).strftime('%Y-%m-%d'): 0.78,
        (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'): 0.85,
        (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'): 0.90,
    }

    return render_template('analytics.html', stats=stats, historical_occupancy=historical_occupancy)

# --- Inteligencia Artificial Exploratoria (Recomendación Simple) ---
@app.route('/recommend', methods=('GET', 'POST'))
def recommend_room():
    recommended_room = None
    if request.method == 'POST':
        preference = request.form.get('preference')
        budget = request.form.get('budget', type=float)

        conn = get_db_connection()
        if conn is None:
            return render_template('recommend.html', recommended_room=None, flash_message='Error de conexión a la BD.', flash_category='error')
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM rooms WHERE is_available = TRUE"
        params = []

        if preference and preference != 'any':
            query += " AND room_type = %s"
            params.append(preference)
        if budget:
            query += " AND price <= %s"
            params.append(budget)

        query += " ORDER BY price ASC LIMIT 1" # Ordena por precio para una recomendación simple

        try:
            cursor.execute(query, params)
            recommended_room = cursor.fetchone()
            if recommended_room:
                flash('Recomendación encontrada!', 'success')
            else:
                flash('No se encontraron habitaciones disponibles con esas preferencias.', 'info')
        except mysql.connector.Error as err:
            flash(f'Error al obtener recomendación: {err}', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('recommend.html', recommended_room=recommended_room)


if __name__ == '__main__':
    app.run(debug=True) # debug=True para desarrollo, se reinicia con cambios y muestra errores