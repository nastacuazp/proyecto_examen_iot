#include <stdio.h>
#include "shell.h"
#include "msg.h"
#include "net/gnrc/netif.h"
#include "net/netopt.h"

#define MAIN_QUEUE_SIZE     (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

/* Función para configurar el canal de las interfaces inalámbricas */
void set_wifi_channel(void) {
    gnrc_netif_t *netif = gnrc_netif_iter(NULL); // Obtener la primera interfaz
    int channel = 6; // Cambia a 11 si prefieres ese canal
    while (netif) {
        if (gnrc_netapi_set(netif->pid, NETOPT_CHANNEL, 0, &channel, sizeof(channel)) < 0) {
            printf("Error al configurar el canal en la interfaz %d\n", netif->pid);
        } else {
            printf("Canal configurado correctamente en la interfaz %d: %d\n", netif->pid, channel);
        }
        netif = gnrc_netif_iter(netif); // Iterar a la siguiente interfaz
    }
}

int main(void) {
    /* Configurar el canal inalámbrico */
    set_wifi_channel();

    /* Inicializar la cola de mensajes */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);
    puts("RIOT border router example application");

    /* Iniciar el shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* Esto nunca debería alcanzarse */
    return 0;
}

