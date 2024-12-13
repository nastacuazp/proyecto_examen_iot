# Sistema IoT para Monitoreo Ambiental

¡Bienvenidos! Somos estudiantes de Ingeniería en Telecomunicaciones de la Universidad Técnica del Norte. Nuestro equipo está conformado por Ariel David Gonzales Bueno, Jordan Raúl Manguay Chacua, Anthony Esteban Ibujes Tupiza, Pablo Alexander Nastacuaz Padilla y Cristopher Alexander Ruales Armijos. Este proyecto implementa un sistema para capturar datos ambientales con sensores DHT11, procesados por ESP32 y retransmitidos mediante un router de borde basado en tecnología IEEE 802.11 hacia un servidor web.

## Introducción

Este sistema consta de nodos sensores basados en ESP32 que recolectan datos de temperatura y humedad usando sensores DHT11. La arquitectura modular permite escalar fácilmente la red, incorporando más nodos o sensores según las necesidades. La información recolectada se transmite a través del estándar IEEE 802.11 hacia un router de borde, que actúa como enlace hacia un servidor web central.

### Tecnologías empleadas

- **IEEE 802.11**: Protocolo estándar para conectividad inalámbrica.
- **HTTP**: Protocolo cliente-servidor para la transferencia de datos.
- **UDP**: Protocolo ligero y no orientado a conexión para la transmisión de datos.
- **UHCP**: Protocolo liviano para asignación de direcciones IP y configuración básica.

## Topología del Sistema

### Nodos Sensores (Clientes)
**Hardware**:
- ESP32-WROOM
- Sensor DHT11

**Software**:
- RIOT OS: Gestión de la red y transmisión de datos.
- Controladores para el sensor DHT11 y manejo de GPIO.

### Router de Borde
**Hardware**:
- ESP32 actuando como puente entre la red local y la global.

**Software**:
- RIOT OS: Configuración de interfaces IPv6 (local y global).

### Servidor Web
**Funcionalidad**:
- Procesamiento y almacenamiento de datos enviados por los nodos.
- Visualización de datos en tiempo real mediante una interfaz web.

**Acceso Remoto**:
- Consultar datos ambientales de manera centralizada.

## Conexión del Sensor DHT11 al ESP32

- **VCC**: Conectar a 3.3V del ESP32.
- **GND**: Conectar a GND del ESP32.
- **DATA**: Conectar al pin GPIO4 del ESP32.

## Documentación Detallada

Para más detalles sobre el proceso de implementación, consulta la documentación completa [aquí](https://www.hackster.io/527576/sistema-de-monitoreo-ambiental-con-sensor-dht11-esp32-042fad?auth_token=95395441f291313b32ccad79eaf4570f).

---
