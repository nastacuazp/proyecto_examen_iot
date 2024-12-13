import mysql.connector
import socket
import re
from datetime import datetime

# Configuración de la conexión a la base de datos
base_de_datos = mysql.connector.connect(
    host="localhost",
    user="USUARIO_BD",                    # MODIFICAR: Reemplazar USUARIO_BD con el nombre de usuario real de la base de datos
    password="CONTRASEÑA_BD",             # MODIFICAR: Reemplazar CONTRASEÑA_BD con la contraseña real de la base de datos
    database="NOMBRE_BD"                  # MODIFICAR: Reemplazar NOMBRE_BD con el nombre real de la base de datos
)

cursor = base_de_datos.cursor()

# Configuración del servidor UDP
IP_SERVIDOR = "DIRECCION_IP_SERVIDOR"  # MODIFICAR: Reemplazar DIRECCION_IP_SERVIDOR con la dirección IP real para IPv6 de la interfaz tap0
PUERTO_SERVIDOR = 8888         # MODIFICAR: Modificar si es necesario usar un puerto diferente
TAMANO_BUFFER = 1024

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

# Crear socket UDP
socket_servidor = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
socket_servidor.bind((IP_SERVIDOR, PUERTO_SERVIDOR))
print(f"Servidor escuchando en [{IP_SERVIDOR}]:{PUERTO_SERVIDOR}")

# Escuchar y almacenar los datos
try:
    while True:
        datos, direccion = socket_servidor.recvfrom(TAMANO_BUFFER)
        print(f"Datos recibidos de {direccion}: {datos.decode()}")

        # Analizar los datos recibidos
        datos_analizados = analizar_datos(datos.decode())
        if datos_analizados:
            numero_nodo, nombre, temperatura, humedad = datos_analizados
            # Obtener la fecha y hora actual
            marca_de_tiempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insertar los datos en la base de datos
            consulta = """
                INSERT INTO datos_sensor (numero_nodo, nombre, temperatura, humedad, marca_de_tiempo)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(consulta, (numero_nodo, nombre, temperatura, humedad, marca_de_tiempo))
            base_de_datos.commit()
            print(f"Datos guardados en la base de datos: {datos_analizados}")
        else:
            print("Formato de datos no válido.")
except KeyboardInterrupt:
    print("Cerrando servidor...")
    socket_servidor.close()
    base_de_datos.close()

