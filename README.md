# 📘 ALLIN I/O 8 — Intégration Home Assistant  
**Contrôleur de relais ALLIN, intégration locale 100% autonome**

---

## 🔧 Présentation

**ALLIN I/O 8** est une intégration Home Assistant permettant de piloter directement les **8 relais** du contrôleur matériel ALLIN.  
Elle est **entièrement locale**, simple, rapide, sans cloud, et pensée pour un usage fiable dans les installations embarquées, autonomes ou domotiques.

L’intégration expose chaque relais comme une **entité `switch`** dans Home Assistant, permettant l’automatisation et le contrôle depuis l’interface utilisateur.

---

## 🚀 Fonctionnalités

### ✔️ Contrôle complet des relais
- Allumer / éteindre chaque relais individuellement  
- Rafraîchissement automatique de l’état toutes les 30 secondes  
- Communication locale directe avec le module ALLIN

### ✔️ Installation simple
- Intégration personnalisée via `custom_components`  
- Détection dans “Ajouter une intégration” sous le nom **ALLIN I/O 8**  
- Aucune configuration YAML nécessaire (config flow via l’UI)

### ✔️ Fiabilité Home Assistant
- Utilisation d’un `DataUpdateCoordinator` pour centraliser les mises à jour  
- Le module ALLIN est exposé comme **Appareil** dans Home Assistant  
- Chaque relais est exposé comme une entité `switch`  
- Gestion des erreurs de connexion et d’authentification pendant la configuration

### ✔️ 100% local
- Aucun service cloud requis  
- Fonctionne en environnement offline (van, bateau, site isolé…)  
- Idéal pour les systèmes autonomes, véhicules de loisirs, etc.

---

## 📦 Installation

### 🛠️ Méthode : manuel via `custom_components`

1. **Télécharger** la dernière version du projet (archive ZIP) depuis le dépôt GitHub.
2. **Extraire** l’archive en local.
3. **Copier** le dossier :

   ```text
   custom_components/allin_io_8
   ```

   dans le répertoire `config` de ton Home Assistant, par exemple :

   ```text
   /config/custom_components/allin_io_8
   ```

4. **Redémarrer** Home Assistant.
5. Aller dans **Paramètres → Appareils & services → Ajouter une intégration**.
6. Rechercher **ALLIN I/O 8** et suivre l’assistant de configuration.

---

## ⚙️ Configuration

Lors de l’ajout de l’intégration, Home Assistant te demande :

| Champ                    | Description                                    |
|--------------------------|------------------------------------------------|
| **Adresse IP / Host**    | Adresse IP ou hostname du module ALLIN (ex: `192.168.1.50`) |
| **Nom d’utilisateur**    | Identifiant de connexion (si authentification activée) |
| **Mot de passe**         | Mot de passe d’accès à l’interface / API      |

Pendant la configuration, l’intégration :

- teste la connexion au module ALLIN,
- valide les identifiants,
- récupère la liste des relais,
- crée automatiquement les entités `switch`.

En cas de problème, des messages d’erreur explicites sont affichés :

- `cannot_connect` → impossible de joindre le module  
- `invalid_auth` → identifiants incorrects  
- `unknown` → erreur inattendue

---

## 🔌 Entités créées

Pour un contrôleur ALLIN I/O 8 standard, Home Assistant crée typiquement :

```text
switch.relay_1
switch.relay_2
switch.relay_3
switch.relay_4
switch.relay_5
switch.relay_6
switch.relay_7
switch.relay_8
```

Chaque entité `switch` représente un relais physique.

### Propriétés principales

- `is_on` : état du relais (activé / désactivé)
- `turn_on` / `turn_off` : commandes d’activation / désactivation
- Regroupement dans l’onglet **Appareils** sous l’appareil : `ALLIN I/O 8 (IP)`.

---

## 🧩 Structure de l’intégration

```text
custom_components/allin_io_8/
│
├── __init__.py          → Initialisation de l’intégration, hub, coordinator
├── config_flow.py       → Config flow (UI) pour l’ajout de l’intégration
├── switch.py            → Déclaration des entités relais (SwitchEntity)
├── const.py             → Constantes (DOMAIN, clés de config, manufacturer…)
├── manifest.json        → Métadonnées Home Assistant (nom, version, dépendances)
├── strings.json         → Clés communes Home Assistant
└── translations/
    ├── en.json          → Traductions anglaises
    └── fr.json          → Traductions françaises
```

---

## ❗ Dépannage

### 🔴 Impossible de se connecter

Symptômes : message d’erreur `cannot_connect` pendant le config flow.

Vérifier :

- l’adresse IP / hostname du module ALLIN ;
- que le module répond bien sur le réseau (ping ou navigation HTTP) ;
- que Home Assistant est sur le même réseau (LAN, VLAN, etc.).

Exemple de test rapide depuis un navigateur :

```text
http://<adresse_ip_du_module>
```

---

### 🔴 Mauvais identifiants (`invalid_auth`)

Symptômes : message d’erreur `invalid_auth` pendant la configuration.

Vérifier :

- le nom d’utilisateur configuré sur le module ALLIN ;
- le mot de passe associé ;
- qu’il n’y a pas de caractère spécial mal saisi (espace en trop, copie-coller, etc.).

Tu peux ensuite relancer le config flow dans Home Assistant.

---

### 🔴 Problème de mise à jour des états

Si les relais ne semblent pas se mettre à jour correctement dans l’UI :

1. Vérifier les journaux de Home Assistant :  
   **Paramètres → Système → Journaux**.
2. Vérifier que le module ALLIN renvoie bien un état de relais exploitable par l’intégration.
3. Si nécessaire, ouvrir une issue sur le dépôt avec :
   - la version de Home Assistant,
   - la version de l’intégration,
   - un extrait de log pertinent.

---

## 🧪 Environnements ciblés

Cette intégration est pensée pour fonctionner avec :

- **Home Assistant OS**
- **Home Assistant Core**
- **Home Assistant en Docker**
- Installations fixes ou embarquées (véhicules, ateliers, sites isolés…)

---

## 📜 Licence

Tu peux préciser ici la licence de ton choix, par exemple :

- Apache 2.0

---

## 🤝 Contributions

Les contributions sont les bienvenues !

Tu peux proposer :

- des améliorations du code,
- un support avancé (modes impulsionnels, temporisation, inversion de logique…),
- un flux d’options pour personnaliser le comportement,
- une meilleure UX (nommage automatisé, regroupements, icônes personnalisées),
- une intégration HACS officielle.

N’hésite pas à ouvrir une **issue** ou une **pull request** sur le dépôt GitHub.
