# Nombre de la aplicación
APPLICATION = dht11_client

# Si no se encuentra una tarjeta en el entorno, utiliza esta por defecto:
BOARD ?= esp32-wroom-32

# Esto tiene que ser la ruta absoluta al directorio base de RIOT:
RIOTBASE ?= $(CURDIR)/../..

# Configurar el canal WiFi
WIFI_CHANNEL ?= 6
CFLAGS += -DWIFI_CHANNEL=$(WIFI_CHANNEL)
DEFAULT_CHANNEL = 6


# Habilitar modo desarrollo
CFLAGS += -DDEVELHELP

# Configuración de compilación
QUIET ?= 1

# Módulos para la red y el shell
USEMODULE += shell
USEMODULE += shell_cmds_default
USEMODULE += shell_cmd_gnrc_udp
USEMODULE += netstats_ipv6
USEMODULE += ps
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6_default
USEMODULE += gnrc_icmpv6_echo
USEMODULE += gnrc_sock_udp
USEMODULE += gnrc_rpl
USEMODULE += auto_init_gnrc_rpl
USEMODULE += netstats_l2
USEMODULE += netstats_rpl
USEMODULE += esp_now
USEMODULE += gnrc_dhcpv6_client_6lbr
USEMODULE += netdev_default
USEMODULE += gnrc_icmpv6_error

# Módulos para el sensor DHT11
USEMODULE += dht
USEMODULE += periph_gpio
USEMODULE += xtimer



# Include de Makefile estándar de RIOT
include $(RIOTBASE)/Makefile.include

