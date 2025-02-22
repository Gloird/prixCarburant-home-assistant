import logging
import sys
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.entity import Entity

ATTR_ID = "station_id"
ATTR_GASOIL = 'gasoil'
ATTR_E95 = 'e95'
ATTR_E98 = 'e98'
ATTR_E10 = 'e10'
ATTR_GPL = 'gplc'
ATTR_E85 = 'e85'
ATTR_GASOIL_LAST_UPDATE = 'last_update_gasoil'
ATTR_E95_LAST_UPDATE = 'last_update_e95'
ATTR_E98_LAST_UPDATE = 'last_update_e98'
ATTR_E10_LAST_UPDATE = 'last_update_e10'
ATTR_GPL_LAST_UPDATE = 'last_update_gplc'
ATTR_E85_LAST_UPDATE = 'last_update_e85'
ATTR_ADDRESS = "station_address"
ATTR_NAME = "station_name"
ATTR_LAST_UPDATE = "last_update"
ATTR_LONGITUDE = "longitude"
ATTR_LATITUDE = "latitude"

CONF_MAX_KM = 'maxDistance'
CONF_SCAN_INTERVAL = 'scanInterval'
CONF_STATION_ID = 'stationID'

SCAN_INTERVAL = timedelta(seconds=3600)


# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MAX_KM, default=10): cv.positive_int,
    vol.Optional(CONF_SCAN_INTERVAL, default=3600): cv.positive_int,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_STATION_ID, default=[]): cv.ensure_list
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    from prixCarburantGloirdClient.prixCarburantGloirdClient import \
        PrixCarburantGloirdClient
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("[prixCarburantLoad] start")
    """Configurer la plate-forme de capteurs."""
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    maxDistance = config.get(CONF_MAX_KM)
    listToExtract = config.get(CONF_STATION_ID)
    scanInterval = config.get(CONF_SCAN_INTERVAL)

    if not scanInterval:
        logging.info("[prixCarburantLoad] pas d'interval custom - 1h")
    else:
        logging.info(
            "[prixCarburantLoad] interval positionner à "+str(scanInterval))
        SCAN_INTERVAL = timedelta(scanInterval)

    homeLocation = [{
        'lat': str(latitude),
        'lng': str(longitude)
    }]

    client = PrixCarburantGloirdClient(homeLocation, maxDistance)
    client.load()

    if not listToExtract:
        logging.info(
            "[prixCarburantLoad] Pas de liste de stations, trouver la station la plus proche")
        stations = client.foundNearestStation()
    else:
        logging.info(
            "[prixCarburantLoad] La liste des stations est définie, extraction en cours")
        list = []
        for station in listToExtract:
            list.append(str(station))
            logging.info("[prixCarburantLoad] - " + str(station))
        stations = client.extractSpecificStation(list)

    logging.info("[prixCarburantLoad] " +
                 str(len(stations)) + " stations trouvées")
    client.clean()
    add_devices([UpdatePrix(client)])
    for station in stations:
        add_devices(
            [PrixCarburant(stations.get(station), client, "mdi:currency-eur"), PrixGazoil(stations.get(station), client, "mdi:currency-eur"), PrixE10(stations.get(station), client, "mdi:currency-eur"), PrixE95(stations.get(station), client, "mdi:currency-eur")])


class UpdatePrix(Entity):
    """Représentation d'un capteur."""

    def __init__(self, client):
        """Initialiser le capteur."""

        logging.info("[updatePrix][UPDATE] Création du sensor")
        self._state = None
        self.client = client
        self._icon = "mdi:refresh-auto"
        self.lastUpdate = self.client.lastUpdate
        self._unique_id = "UpdatePrix"

    @property
    def name(self):
        """Renvoie le nom du capteur."""
        return "UpdatePrix"

    @property
    def state(self):
        """Renvoyer l'état du capteur."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Renvoyer l'unité de mesure."""
        return "date_time"

    @property
    def unique_id(self) -> str:
        """Renvoie l'identifiant unique de ce capteur."""
        return 123

    @property
    def icon(self) -> str:
        """Renvoie l'icône mdi de l'entité."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Renvoyer les attributs d'état de l'appareil de la dernière mise à jour."""

        attrs = {}
        return attrs

    def update(self):
        """Récupérer de nouvelles données d'état pour le capteur.

         C'est la seule méthode qui devrait récupérer de nouvelles données pour Home Assistant.
        """

        self.client.load()
        logging.info("[updatePrix][UPDATE] mise a jour des prix")

        if self.lastUpdate != self.client.lastUpdate:
            logging.info(
                "[updatePrix][UPDATE] les données on changer - " + str(self.lastUpdate))

        self.lastUpdate = self.client.lastUpdate

        self._state = self.lastUpdate
        self.client.clean()


class PrixGazoil(Entity):
    """Représentation d'un capteur."""

    def __init__(self, station, client, icon):
        """Initialiser le capteur."""

        logging.info("[prixCarburantLoad][UPDATE][" +
                     station.id+"_gazoil] Création du sensor")
        self._state = None
        self.station = station
        self.client = client
        self._icon = icon
        self._state = self.station.gazoil['valeur']
        self.lastUpdate = self.client.lastUpdate
        self.lastUpdateTech = self.client.lastUpdate
        self._unique_id = "PrixCarburant_" + self.station.id+"_gazoil"

    @property
    def name(self):
        """Renvoie le nom du capteur."""
        return "PrixCarburant_" + self.station.id+"_gazoil"

    @property
    def state(self):
        """Renvoyer l'état du capteur."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Renvoyer l'unité de mesure."""
        return "€"

    @property
    def unique_id(self) -> str:
        """Renvoie l'identifiant unique de ce capteur."""
        return f"{self._unique_id}"

    @property
    def icon(self) -> str:
        """Renvoie l'icône mdi de l'entité."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Renvoyer les attributs d'état de l'appareil de la dernière mise à jour."""

        attrs = {
            ATTR_ID: self.station.id,
            ATTR_GASOIL: self.station.gazoil['valeur'],
            ATTR_GASOIL_LAST_UPDATE: self.station.gazoil['maj'],
            ATTR_ADDRESS: self.station.adress,
            ATTR_NAME: self.station.name,
            ATTR_LONGITUDE: self.station.longitude,
            ATTR_LATITUDE: self.station.latitude,
            ATTR_LAST_UPDATE: self.client.lastUpdate.strftime(
                '%Y-%m-%d %H:%M:%S')
        }
        logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                     "_gazoil] Mise a jour des attrs - "+str(attrs))
        return attrs

    def update(self):
        """Récupérer de nouvelles données d'état pour le capteur.

         C'est la seule méthode qui devrait récupérer de nouvelles données pour Home Assistant.
        """

        self.client.reloadIfNecessary()
        logging.info("[prixCarburantLoad][UPDATE][" +
                     self.station.id+"_gazoil] mise a jour du sensor")
        list = []
        list.append(str(self.station.id))
        myStation = self.client.extractSpecificStation(list)
        self.station = myStation.get(self.station.id)
        if self.lastUpdate != self.client.lastUpdate:
            logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                         "_gazoil] les données on changer - " + str(self.lastUpdate))

        self.lastUpdate = self.client.lastUpdate

        self._state = self.station.gazoil['valeur']
        self.client.clean()


class PrixE95(Entity):
    """Représentation d'un capteur."""

    def __init__(self, station, client, icon):
        """Initialiser le capteur."""

        logging.info("[prixCarburantLoad][UPDATE][" +
                     station.id+"_e95] Création du sensor")
        self._state = None
        self.station = station
        self.client = client
        self._icon = icon
        self._state = self.station.e95['valeur']
        self.lastUpdate = self.client.lastUpdate
        self.lastUpdateTech = self.client.lastUpdate
        self._unique_id = "PrixCarburant_" + self.station.id+"_e95"

    @property
    def name(self):
        """Renvoie le nom du capteur."""
        return "PrixCarburant_" + self.station.id+"_e95"

    @property
    def state(self):
        """Renvoyer l'état du capteur."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Renvoyer l'unité de mesure."""
        return "€"

    @property
    def unique_id(self) -> str:
        """Renvoie l'identifiant unique de ce capteur."""
        return f"{self._unique_id}"

    @property
    def icon(self) -> str:
        """Renvoie l'icône mdi de l'entité."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Renvoyer les attributs d'état de l'appareil de la dernière mise à jour."""

        attrs = {
            ATTR_ID: self.station.id,
            ATTR_E95: self.station.e95['valeur'],
            ATTR_E95_LAST_UPDATE: self.station.e95['maj'],
            ATTR_ADDRESS: self.station.adress,
            ATTR_NAME: self.station.name,
            ATTR_LONGITUDE: self.station.longitude,
            ATTR_LATITUDE: self.station.latitude,
            ATTR_LAST_UPDATE: self.client.lastUpdate.strftime(
                '%Y-%m-%d %H:%M:%S')
        }
        logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                     "_e95] Mise a jour des attrs - "+str(attrs))
        return attrs

    def update(self):
        """Récupérer de nouvelles données d'état pour le capteur.

         C'est la seule méthode qui devrait récupérer de nouvelles données pour Home Assistant.
        """

        self.client.reloadIfNecessary()
        logging.info("[prixCarburantLoad][UPDATE][" +
                     self.station.id+"_e95] mise a jour du sensor")
        list = []
        list.append(str(self.station.id))
        myStation = self.client.extractSpecificStation(list)
        self.station = myStation.get(self.station.id)
        if self.lastUpdate != self.client.lastUpdate:
            logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                         "_e95] les données on changer - " + str(self.lastUpdate))

        self.lastUpdate = self.client.lastUpdate

        self._state = self.station.e95['valeur']
        self.client.clean()


class PrixE10(Entity):
    """Représentation d'un capteur."""

    def __init__(self, station, client, icon):
        """Initialiser le capteur."""

        logging.info("[prixCarburantLoad][UPDATE][" +
                     station.id+"_e10] Création du sensor")
        self._state = None
        self.station = station
        self.client = client
        self._icon = icon
        self._state = self.station.e10['valeur']
        self.lastUpdate = self.client.lastUpdate
        self.lastUpdateTech = self.client.lastUpdate
        self._unique_id = "PrixCarburant_" + self.station.id+"_e10"

    @property
    def name(self):
        """Renvoie le nom du capteur."""
        return "PrixCarburant_" + self.station.id+"_e10"

    @property
    def state(self):
        """Renvoyer l'état du capteur."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Renvoyer l'unité de mesure."""
        return "€"

    @property
    def unique_id(self) -> str:
        """Renvoie l'identifiant unique de ce capteur."""
        return f"{self._unique_id}"

    @property
    def icon(self) -> str:
        """Renvoie l'icône mdi de l'entité."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Renvoyer les attributs d'état de l'appareil de la dernière mise à jour."""

        attrs = {
            ATTR_ID: self.station.id,
            ATTR_E10: self.station.e10['valeur'],
            ATTR_E10_LAST_UPDATE: self.station.e10['maj'],
            ATTR_ADDRESS: self.station.adress,
            ATTR_NAME: self.station.name,
            ATTR_LONGITUDE: self.station.longitude,
            ATTR_LATITUDE: self.station.latitude,
            ATTR_LAST_UPDATE: self.client.lastUpdate.strftime(
                '%Y-%m-%d %H:%M:%S')
        }
        logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                     "_e10] Mise a jour des attrs - "+str(attrs))
        return attrs

    def update(self):
        """Récupérer de nouvelles données d'état pour le capteur.

         C'est la seule méthode qui devrait récupérer de nouvelles données pour Home Assistant.
        """

        self.client.reloadIfNecessary()
        logging.info("[prixCarburantLoad][UPDATE][" +
                     self.station.id+"_e10] mise a jour du sensor")
        list = []
        list.append(str(self.station.id))
        myStation = self.client.extractSpecificStation(list)
        self.station = myStation.get(self.station.id)
        if self.lastUpdate != self.client.lastUpdate:
            logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                         "_e10] les données on changer - " + str(self.lastUpdate))

        self.lastUpdate = self.client.lastUpdate

        self._state = self.station.e10['valeur']
        self.client.clean()


class PrixCarburant(Entity):
    """Représentation d'un capteur."""

    def __init__(self, station, client, icon):
        """Initialiser le capteur."""

        logging.info("[prixCarburantLoad][UPDATE][" +
                     station.id+"] Création du sensor")
        self._state = None
        self.station = station
        self.client = client
        self._icon = icon
        self._state = self.station.gazoil['valeur']
        self.lastUpdate = self.client.lastUpdate
        self.lastUpdateTech = self.client.lastUpdate
        self._unique_id = "PrixCarburant_" + self.station.id

    @property
    def name(self):
        """Renvoie le nom du capteur."""
        return 'PrixCarburant_' + self.station.id

    @property
    def state(self):
        """Renvoyer l'état du capteur."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Renvoyer l'unité de mesure."""
        return "€"

    @property
    def unique_id(self) -> str:
        """Renvoie l'identifiant unique de ce capteur."""
        return f"{self._unique_id}"

    @property
    def icon(self) -> str:
        """Renvoie l'icône mdi de l'entité."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Renvoyer les attributs d'état de l'appareil de la dernière mise à jour."""

        attrs = {
            ATTR_ID: self.station.id,
            ATTR_GASOIL: self.station.gazoil['valeur'],
            ATTR_GASOIL_LAST_UPDATE: self.station.gazoil['maj'],
            ATTR_E95: self.station.e95['valeur'],
            ATTR_E95_LAST_UPDATE: self.station.e95['maj'],
            ATTR_E98: self.station.e98['valeur'],
            ATTR_E98_LAST_UPDATE: self.station.e98['maj'],
            ATTR_E10: self.station.e10['valeur'],
            ATTR_E10_LAST_UPDATE: self.station.e10['maj'],
            ATTR_E85: self.station.e85['valeur'],
            ATTR_E85_LAST_UPDATE: self.station.e85['maj'],
            ATTR_GPL: self.station.gpl['valeur'],
            ATTR_GPL_LAST_UPDATE: self.station.gpl['maj'],
            ATTR_ADDRESS: self.station.adress,
            ATTR_NAME: self.station.name,
            ATTR_LONGITUDE: self.station.longitude,
            ATTR_LATITUDE: self.station.latitude,
            ATTR_LAST_UPDATE: self.client.lastUpdate.strftime(
                '%Y-%m-%d %H:%M:%S')
        }
        logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                     "] Mise a jour des attrs - "+str(attrs))
        return attrs

    def update(self):
        """Récupérer de nouvelles données d'état pour le capteur.

         C'est la seule méthode qui devrait récupérer de nouvelles données pour Home Assistant.
        """

        self.client.reloadIfNecessary()
        logging.info("[prixCarburantLoad][UPDATE][" +
                     self.station.id+"] mise a jour du sensor")
        list = []
        list.append(str(self.station.id))
        myStation = self.client.extractSpecificStation(list)
        self.station = myStation.get(self.station.id)
        if self.lastUpdate != self.client.lastUpdate:
            logging.info("[prixCarburantLoad][UPDATE]["+self.station.id +
                         "] les données on changer - " + str(self.lastUpdate))

        self.lastUpdate = self.client.lastUpdate

        self._state = self.station.gazoil['valeur']
        self.client.clean()
