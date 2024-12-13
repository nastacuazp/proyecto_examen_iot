import flask
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import mysql.connector
from datetime import datetime, timedelta
import threading
import socket
import re
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Configuración de la conexión a la base de datos
base_de_datos = mysql.connector.connect(
    host="localhost",
    user="USUARIO_BD",                    # MODIFICAR: Reemplazar USUARIO_BD con el nombre de usuario real de la base de datos
    password="CONTRASEÑA_BD",             # MODIFICAR: Reemplazar CONTRASEÑA_BD con la contraseña real de la base de datos
    database="NOMBRE_BD"                  # MODIFICAR: Reemplazar NOMBRE_BD con el nombre real de la base de datos
)

@app.route('/')
def indice():
    return render_template('index.html')

@app.route('/api/datos')
def obtener_datos():
    cursor = base_de_datos.cursor(dictionary=True)
    
    fecha_inicio = request.args.get('fecha_inicio', default=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'))
    fecha_fin = request.args.get('fecha_fin', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    consulta = """
    SELECT numero_nodo, nombre, temperatura, humedad, marca_de_tiempo 
    FROM datos_sensor 
    WHERE marca_de_tiempo BETWEEN %s AND %s AND numero_nodo IN (1, 2, 3, 4)
    ORDER BY marca_de_tiempo DESC
    """
    
    cursor.execute(consulta, (fecha_inicio, fecha_fin))
    
    filas = cursor.fetchall()
    cursor.close()
    return jsonify(filas)

# Función para analizar los datos recibidos
def analizar_datos(datos):
    coincidencia = re.match(r"Nodo (\d+) $$(.+?)$$ - Temp: ([\d.]+)°C, Humedad: ([\d.]+)%", datos)
    if coincidencia:
        numero_nodo = int(coincidencia.group(1))
        nombre = coincidencia.group(2)
        temperatura = float(coincidencia.group(3))
        humedad = float(coincidencia.group(4))
        return numero_nodo, nombre, temperatura, humedad
    return None

def hilo_servidor_udp():
    # Configuración del servidor UDP
    IP_SERVIDOR = "DIRECCION_IP_SERVIDOR"     # MODIFICAR: Reemplazar DIRECCION_IP_SERVIDOR con la dirección IP real para IPv6 de la interfaz tap0
    PUERTO_SERVIDOR = 8888            # MODIFICAR: Modificar si es necesario usar un puerto diferente
    TAMANO_BUFFER = 1024

    # Crear socket UDP
    socket_servidor = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    socket_servidor.bind((IP_SERVIDOR, PUERTO_SERVIDOR))
    print(f"Servidor UDP escuchando en [{IP_SERVIDOR}]:{PUERTO_SERVIDOR}")

    # Escuchar y almacenar los datos
    while True:
        try:
            datos, direccion = socket_servidor.recvfrom(TAMANO_BUFFER)
            print(f"Datos recibidos de {direccion}: {datos.decode()}")

            # Analizar los datos recibidos
            datos_analizados = analizar_datos(datos.decode())
            if datos_analizados:
                numero_nodo, nombre, temperatura, humedad = datos_analizados
                # Obtener la fecha y hora actual
                marca_de_tiempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Insertar los datos en la base de datos
                cursor = base_de_datos.cursor()
                consulta = """
                    INSERT INTO datos_sensor (numero_nodo, nombre, temperatura, humedad, marca_de_tiempo)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(consulta, (numero_nodo, nombre, temperatura, humedad, marca_de_tiempo))
                base_de_datos.commit()
                cursor.close()

                print(f"Datos guardados en la base de datos: {datos_analizados}")
                
                # Emitir los datos a través de WebSocket
                ultimos_datos = {
                    'numero_nodo': numero_nodo,
                    'nombre': nombre,
                    'temperatura': temperatura,
                    'humedad': humedad,
                    'marca_de_tiempo': marca_de_tiempo
                }
                socketio.emit('nuevos_datos', ultimos_datos)

            else:
                print("Formato de datos no válido.")
        except Exception as e:
            print(f"Error en el servidor UDP: {e}")
            time.sleep(1)

def hilo_fondo():
    while True:
        try:
            cursor = base_de_datos.cursor(dictionary=True)
            consulta = """
            SELECT numero_nodo, nombre, temperatura, humedad, marca_de_tiempo 
            FROM datos_sensor 
            ORDER BY marca_de_tiempo DESC 
            LIMIT 1
            """
            cursor.execute(consulta)
            ultimos_datos = cursor.fetchone()
            cursor.close()
            
            if ultimos_datos:
                socketio.emit('nuevos_datos', ultimos_datos)
            
            time.sleep(1)  # Esperar 1 segundo antes de la próxima actualización
        except Exception as e:
            print(f"Error en el hilo de fondo: {e}")
            time.sleep(1)

@socketio.on('connect')
def manejar_conexion():
    print("Cliente conectado")

def iniciar_servidor_udp():
    hilo_udp = threading.Thread(target=hilo_servidor_udp, daemon=True)
    hilo_udp.start()

def iniciar_hilo_fondo():
    hilo_bg = threading.Thread(target=hilo_fondo, daemon=True)
    hilo_bg.start()

if __name__ == '__main__':
    # Iniciar el servidor UDP en un hilo separado
    iniciar_servidor_udp()
    
    # Iniciar el hilo de fondo para actualizaciones
    iniciar_hilo_fondo()
    
    # Ejecutar la aplicación Flask
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

