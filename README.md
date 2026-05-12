# 📘 ALLIN I/O 8 — Intégration Home Assistant  
**Contrôleur de relais ALLIN, intégration locale 100% autonome**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz/)

---

## 🔧 Présentation

**ALLIN I/O 8** est une intégration Home Assistant permettant de piloter directement les **8 relais** du contrôleur matériel ALLIN.  
Elle est **entièrement locale**, simple, rapide, sans cloud, et pensée pour un usage fiable dans les installations embarquées, autonomes ou domotiques.

L’intégration expose chaque relais comme une **entité `switch`** dans Home Assistant, permettant l’automatisation et le contrôle depuis l’interface utilisateur.

---

## 🚀 Fonctionnalités

### ✔️ Contrôle complet des relais
- Activation / désactivation de chaque relais  
- Rafraîchissement automatique toutes les 30 secondes  
- Appareil entièrement local, aucune dépendance cloud

### ✔️ Installation simple
- Fonctionne via `custom_components`  
- Ajout via l’interface “Ajouter une intégration”
- Aucun YAML nécessaire

### ✔️ Fiabilité Home Assistant
- `DataUpdateCoordinator` pour les mises à jour d’état  
- Support natif du Device Registry  
- Gestion des erreurs : connexion, identifiants, timeouts

### ✔️ 100% local et offline
- Idéal pour installations embarquées (van, bateau, off-grid)  
- Fonctionnement hors-ligne complet

---

## 📦 Installation

### 🛠️ Installation via HACS (Custom Repository)

1. Ouvrir **HACS → Intégrations**  
2. Cliquer sur **⋮ → Custom repositories**  
3. Ajouter le dépôt :  
   ```
   https://github.com/CarapaceStore/ALLIN-I-O-8
   ```
4. Catégorie : **Integration**  
5. Installer l’intégration via HACS  
6. Redémarrer Home Assistant  
7. Ajouter l’intégration :  
   **Paramètres → Appareils & services → Ajouter une intégration → ALLIN I/O 8**

---

### 🛠️ Installation manuelle

1. Télécharger la dernière release ZIP  
2. Copier dans :  
   ```
   /config/custom_components/allin_io_8
   ```
3. Redémarrer Home Assistant  
4. Ajouter l’intégration depuis l’UI

---

## ⚙️ Configuration

L’assistant demande :

| Champ | Description |
|-------|-------------|
| **Adresse IP / Host** | L’adresse du module ALLIN (ex : `192.168.1.50`) |
| **Nom d’utilisateur** | Identifiant de connexion |
| **Mot de passe** | Mot de passe API |

L’intégration :

- teste la connexion,  
- vérifie l’authentification,  
- découvre les relais,  
- crée automatiquement les entités.

**Erreurs possibles :**

- `cannot_connect` → module injoignable  
- `invalid_auth` → identifiants incorrects  
- `unknown` → erreur imprévue  

---

## 🔌 Entités créées

Chaque relais devient une entité :

```text
switch.relay_1
switch.relay_2
...
switch.relay_8
```

### Attributs

- `is_on` : état du relais  
- `turn_on()` / `turn_off()`  
- Informations device dans l’onglet Appareils

---

## 🏷️ Personnalisation des noms (Options)

Chaque relais peut recevoir un **nom personnalisé** depuis l’interface Home Assistant :

**Paramètres → Appareils & services → ALLIN I/O 8 → ⚙️ Configurer**

Vous pouvez par exemple renommer :
- `Relay 1` → `Pompe à eau`
- `Relay 2` → `Éclairage intérieur`
- `Relay 3` → `Marche électrique`
- …

L’intégration se recharge automatiquement après modification. Les noms sont stockés dans `entry.options` et persistent entre redémarrages.

---

## ⏱️ Service `allin_io_8.pulse`

Active un relais pendant une durée définie, puis le désactive automatiquement. Idéal pour gâches, klaxons, marches électriques.

```yaml
service: allin_io_8.pulse
data:
  entity_id: switch.relay_3
  duration: 2.5   # secondes (0.1 → 60)
```

Disponible aussi depuis **Outils de développement → Services** avec un sélecteur natif HA.

---

## 🔬 Diagnostics

L’intégration supporte le téléchargement de diagnostics natif HA :
**Appareils & services → ALLIN I/O 8 → Télécharger les diagnostics**

Le fichier exporté contient l’état du coordinator, la liste des relais et leur état, avec les identifiants/mots de passe automatiquement masqués.

---

## 🧩 Structure du projet

```text
custom_components/allin_io_8/
│
├── __init__.py          → Init + DataUpdateCoordinator + service pulse
├── config_flow.py       → Configuration UI + OptionsFlow
├── switch.py            → Entités Switch (has_entity_name)
├── diagnostics.py       → Téléchargement de diagnostics
├── const.py             → Constantes
├── manifest.json        → Déclaration Home Assistant
├── services.yaml        → Schéma du service pulse
├── strings.json         → Clés internes HA
└── translations/
    ├── en.json          → Traductions EN
    └── fr.json          → Traductions FR
```

---

## ❗ Dépannage

### 🔴 Impossible de se connecter (`cannot_connect`)
- Vérifier l’adresse IP  
- Tester dans un navigateur :  
  ```
  http://IP_DU_MODULE
  ```
- Vérifier le réseau ou le VLAN

### 🔴 Identifiants incorrects (`invalid_auth`)
- Vérifier username / password définis sur le module  
- Vérifier pas d’espace / erreur de frappe

### 🔴 État non mis à jour
- Vérifier les logs Home Assistant  
- Vérifier que le module renvoie bien l’état de chaque relais

---

## 🧪 Compatibilité

Testé avec :

- Home Assistant OS  
- Home Assistant Core  
- Home Assistant en Docker  
- Installations offline / embarquées

---

## 📜 Licence

Licence open-source MIT

---

## 🤝 Contributions

Les contributions sont bienvenues !

Idées d’amélioration :

- Options avancées (mode pulse, temporisation, inversion logique)  
- Renommage automatique des relais  
- Détection avancée du hardware  
- Publication HACS officielle  

N’hésite pas à ouvrir une issue ou une PR sur le repo 👇  
👉 **https://github.com/CarapaceStore/ALLIN-I-O-8**
