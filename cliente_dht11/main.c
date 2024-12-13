#include <stdio.h>
#include <string.h>
#include "xtimer.h"
#include "dht.h"
#include "dht_params.h"
#include "periph/gpio.h"
#include "net/sock/udp.h"
#include "net/gnrc/netif.h"
#include "net/netdev.h"
#include "msg.h"
#include "shell.h"

#define PIN_LED GPIO_PIN(0, 5)
#define PIN_DHT GPIO_PIN(0, 4)
#define TIPO_DHT DHT11

#define DIRECCION_SERVIDOR "DIRECCION_IP_SERVIDOR"	// MODIFICAR: Reemplazar DIRECCION_IP_SERVIDOR con la dirección IPv6 real del servidor
#define PUERTO_SERVIDOR 8888		        // MODIFICAR: Modificar si es necesario usar un puerto diferente
#define PUERTO_CLIENTE 8888		            // MODIFICAR: Modificar si es necesario usar un puerto diferente para el cliente
#define CANAL_WIFI 6                        // MODIFICAR: Modificar si se necesita usar un canal WiFi diferente

#define TAMANO_MAXIMO_BUFFER 128
#define TAMANO_COLA_PRINCIPAL 8

static msg_t _cola_mensajes_principal[TAMANO_COLA_PRINCIPAL];
static dht_t sensor_dht;
static uint8_t buffer[TAMANO_MAXIMO_BUFFER];

// Configura el canal WiFi
static void configurar_canal_wifi(void) {
    gnrc_netif_t *interfaz_red = gnrc_netif_iter(NULL);
    if (interfaz_red != NULL) {
        netdev_t *dispositivo = interfaz_red->dev;
        if (dispositivo != NULL) {
            netopt_enable_t habilitar = NETOPT_ENABLE;
            int canal = CANAL_WIFI;
            dispositivo->driver->set(dispositivo, NETOPT_CHANNEL, &canal, sizeof(canal));
            dispositivo->driver->set(dispositivo, NETOPT_STATE, &habilitar, sizeof(habilitar));
            printf("Canal WiFi configurado en: %d\n", CANAL_WIFI);
        }
    }
}

// Inicializa el sensor DHT11 de manera silenciosa
static int inicializar_dht_silenciosamente(void) {
    dht_params_t parametros = {
        .pin = PIN_DHT,
        .type = TIPO_DHT
    };
    for (int i = 0; i < 5; i++) {
        if (dht_init(&sensor_dht, &parametros) == DHT_OK) {
            return 0;
        }
        xtimer_sleep(1);
    }
    return -1;
}

// Función para el cliente UDP
int cliente_udp(int argc, char **argv) {
    printf("Inicializando cliente UDP...\n");

    configurar_canal_wifi();

    if (inicializar_dht_silenciosamente() != 0) {
        printf("No se pudo inicializar el sensor DHT11\n");
        return -1;
    }
    printf("Sensor DHT11 inicializado correctamente\n");

    sock_udp_ep_t local = SOCK_IPV6_EP_ANY;
    local.port = PUERTO_CLIENTE;

    sock_udp_ep_t remoto = {
        .family = AF_INET6,
        .port = PUERTO_SERVIDOR
    };

    sock_udp_t socket;
    if (sock_udp_create(&socket, &local, NULL, 0) < 0) {
        puts("Error creando socket UDP");
        return -1;
    }

    // Verificar si la dirección IPv6 es válida
    if (ipv6_addr_from_str((ipv6_addr_t *)&remoto.addr.ipv6, DIRECCION_SERVIDOR) == NULL) {
        puts("Error: Dirección IPv6 del servidor no válida");
        return -1;
    } else {
        printf("Conectando a la dirección: %s\n", DIRECCION_SERVIDOR);
    }

    while (1) {
        gpio_set(PIN_LED);
        int16_t temperatura, humedad;

        if (dht_read(&sensor_dht, &temperatura, &humedad) == DHT_OK) {
            float temp_celsius = temperatura / 10.0;
            float hum_porcentaje = humedad / 10.0;
            snprintf((char *)buffer, TAMANO_MAXIMO_BUFFER, "Nodo NUMERO_NODO (NOMBRE_NODO) - Temp: %.1f°C, Humedad: %.1f%%", temp_celsius, hum_porcentaje); 
            // MODIFICAR: Reemplazar NUMERO_NODO con el número real del nodo (por ejemplo, 1, 2, 3, etc.)
            // MODIFICAR: Reemplazar NOMBRE_NODO con el nombre real del nodo (por ejemplo, "Sala", "Cocina", "Dormitorio", etc.)

            if (sock_udp_send(&socket, buffer, strlen((char *)buffer), &remoto) < 0) {
                puts("Error enviando datos del sensor");
            } else {
                printf("Datos enviados: %s\n", buffer);
            }
        } else {
            inicializar_dht_silenciosamente();
        }

        gpio_clear(PIN_LED);
        xtimer_sleep(10); // Retraso para enviar datos al servidor.
    }

    return 0;
}

// Comandos del shell
static const shell_command_t comandos_shell[] = {
    { "cliente_udp", "Inicia cliente UDP con DHT11", cliente_udp },
    { NULL, NULL, NULL }
};

// Función principal para ejecutar la shell y gestionar el cliente UDP
int main(void) {
    gpio_init(PIN_LED, GPIO_OUT);
    msg_init_queue(_cola_mensajes_principal, TAMANO_COLA_PRINCIPAL);

    puts("Nodo cliente con soporte de shell");
    puts("Comandos disponibles: cliente_udp");

    // Ejecutar el shell para permitir comandos
    char buffer_linea[SHELL_DEFAULT_BUFSIZE];
    shell_run(comandos_shell, buffer_linea, SHELL_DEFAULT_BUFSIZE);

    /* Nunca debería alcanzarse este punto */
    return 0;
}

