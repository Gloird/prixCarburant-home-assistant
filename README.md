[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
# prixCarburant-home-assistant
Client python permettant d'interroger l'openData du gouvernement sur le prix du carburant.

https://www.prix-carburants.gouv.fr/

Le client permet de :
 - Trouver les stations les plus proches dans un cercle de X km configurable a partir de votre adresse defini dans home assistant
 - Extraire des stations spécifiques via son ID


Aide à l'installation depuis HACS :

Dans HACS, cliquer sur ... puis depots personnalisés

Ajouter :

- URL : https://github.com/Gloird/prixCarburant-home-assistant
- Catégorie : Intégration

## Configuration
Exemple de configuration :

### Configuration pour récupérer les stations dans un rayon de 20 km
```
sensor:
  platform: prixCarburant
  maxDistance: 20
```

### Configuration pour récupérer les stations très spécifique   
```
sensor:
  platform: prixCarburant
  #maxDistance: 20
  stationID:
    - 59000009
    - 59000080
```


Exemple de données extraites :
```
station_id: 79000001
gasoil: 1.999
last_update_gasoil: 2022-03-14 11:25:37
e95: 1.999
last_update_e95: 2022-03-14 11:25:38
e98: None
last_update_e98: 
e10: 1.949
last_update_e10: 2022-03-14 11:25:38
e85: 0.999
last_update_e85: 2022-03-14 11:25:38
gplc: None
last_update_gplc: 
station_address: 80 Avenue SaintJean d'Angély 79000 NIORT
station_name: Carrefour Market
longitude: -0.466
latitude: 46.318
last_update: 2022-03-15 00:00:00
unit_of_measurement: €
icon: mdi:currency-eur
friendly_name: PrixCarburant_79000001
```

Exemple de donnée pour un type de carburant:

```
station_id: 79000001
e10: 1.949
last_update_e10: 2022-03-14 11:25:38
station_address: 80 Avenue SaintJean d'Angély 79000 NIORT
station_name: Carrefour Market
longitude: -0.466
latitude: 46.318
last_update: 2022-03-15 00:00:00
unit_of_measurement: €
icon: mdi:currency-eur
friendly_name: PrixCarburant_79000001_e10
```

### Configuration d'affichage dans Home Assistant

#### via flex-table-card

Permet d'afficher le prix dans l'ordre

La date d'actualisation des prix est également affichée
```
type: custom:flex-table-card
title: Prix Gasoil
entities:
  include:
    - sensor.prixcarburant_79370001
    - sensor.prixcarburant_79370002
    - sensor.prixcarburant_79000002
    - sensor.prixcarburant_79000008
    - sensor.prixcarburant_79000012
    - sensor.prixcarburant_79230003
sort_by: gasoil
strict: true
clickable: true
columns:
  - data: station_name
    name: Nom
  - data: gasoil
    name: Gasoil
    suffix: ' €'
  - data: last_update_gasoil
    modify: >-
      new Number((Date.now() / 86400000) - (Date.parse(x) /
      86400000)).toFixed(0)
    name: Date
    suffix: ' Jours'
```


#### via carte multiple-entity-row

![alt text](https://forum.hacf.fr/uploads/default/original/2X/5/5bcb6d091aa764431ddb271c3087c7544013c599.png)

```
type: entities
title: Prix carburants
entities:
  - entity: sensor.prixcarburant_79370001
    type: custom:multiple-entity-row
    name: Auchan
    icon: mdi:gas-station
    show_state: false
    entities:
      - attribute: E98
        name: E98
        unit: €
      - attribute: E10
        name: E10
        unit: €
      - attribute: GPLc
        name: GPL
        unit: €
  - entity: sensor.prixcarburant_79370002
    type: custom:multiple-entity-row
    name: E.Leclerc
    icon: mdi:gas-station
    show_state: false
    entities:
```

# Information

Source code du client si vous souhaitez contribuer : "https://github.com/Gloird/essence"

Il s'agit d'un fork de https://github.com/max5962/prixCarburant-home-assistant, mis à jour afin de recuperer le E85 et le GPLc
