"""Constantes pour l'intégration ALLIN I/O 8."""

DOMAIN = "allin_io_8"
MANUFACTURER = "ALLIN"
MODEL = "I/O 8"

# Champs de configuration
CONF_HOSTNAME = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Clés stockage runtime (hass.data[DOMAIN][entry_id])
DATA_COORDINATOR = "coordinator"
DATA_HUB = "hub"
DATA_HOST = "host"

# Paramètres par défaut
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_TIMEOUT = 10

# Nombre de relais sur la carte I/O 8
RELAY_COUNT = 8

# Préfixes des clés d'options de noms personnalisés (relay_1 .. relay_8)
OPTION_RELAY_PREFIX = "relay_"

# Services
SERVICE_PULSE = "pulse"
ATTR_DURATION = "duration"
DEFAULT_PULSE_DURATION = 1.0
