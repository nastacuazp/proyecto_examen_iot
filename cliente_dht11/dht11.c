#include "periph/gpio.h"
#include "xtimer.h"
#include <stdio.h>

// Función para leer los datos del sensor DHT11
int dht11_read(uint8_t pin, int *temperature, int *humidity) {
    uint8_t data[5];
    int i, j;

    // Configura el pin para iniciar la comunicación
    gpio_set(pin);
    gpio_clear(pin);
    xtimer_usleep(20000); // 20 ms de espera para iniciar la comunicación

    // Recibe los 5 bytes de datos
    for (j = 0; j < 5; j++) {
        data[j] = 0;
        for (i = 7; i >= 0; i--) {
            // Espera a que el pin suba
            int wait_count = 0;
            while (!gpio_read(pin) && wait_count < 10000) { // Timeout para evitar bloqueo
                wait_count++;
            }
            if (wait_count >= 10000) {
                return -1; // Error de lectura si el pin no sube a tiempo
            }
            xtimer_usleep(30);  // Espera de 30 microsegundos
            if (gpio_read(pin)) {
                data[j] |= (1 << i);
            }
            while (gpio_read(pin)) {}  // Espera a que el pin vuelva a bajo
        }
    }

    // Verifica la suma de verificación
    if (data[4] != (data[0] + data[1] + data[2] + data[3])) {
        return -1;  // Error en la verificación
    }

    // Convierte los datos a temperatura y humedad
    *humidity = (data[0] << 8) | data[1];
    *temperature = (data[2] << 8) | data[3];

    return 0;  // Éxito
}
