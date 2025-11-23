ALLIN I/O 8 — Intégration Home Assistant

Contrôleur de relais ALLIN, intégration locale 100% autonome

Présentation

ALLIN I/O 8 est une intégration Home Assistant permettant de piloter directement les 8 relais du contrôleur matériel ALLIN.
Elle est entièrement locale, simple, rapide, sans cloud, et pensée pour un usage fiable dans les installations embarquées, autonomes ou domotiques.

L’intégration expose chaque relais comme une entité switch dans Home Assistant, permettant l’automatisation et le contrôle depuis l’interface utilisateur.

Fonctionnalités
Contrôle complet des relais

Allumer / éteindre chaque relais individuellement

Rafraîchissement automatique de l’état toutes les 30 secondes

Basée sur la librairie Python interne (API locale)

Installation simple

Compatible avec le chargement manuel (custom_components)

Apparaît automatiquement dans “Ajouter une intégration”

Fiabilité Home Assistant

Suivi via un DataUpdateCoordinator

Reconnaissance du matériel en tant que device

Entités nommées automatiquement

Gestion des erreurs réseau / authentification pendant le config flow

Totalement locale

Aucun cloud

Aucune dépendance externe

Fonctionne en environnement offline (van, bateau, off-grid…)

Installation
Méthode : Manuel via custom_components

Télécharger la dernière release ZIP :
(Par exemple : ALLIN-I-O-8-main-reviewed.zip)

Extraire son contenu.

Copier le dossier :

custom_components/allin_io_8


dans ton Home Assistant :

/config/custom_components/allin_io_8


Redémarrer Home Assistant.

Aller dans Paramètres → Appareils & Services → Ajouter une intégration
Chercher : ALLIN I/O 8

Configuration

Lors de l’ajout de l’intégration, Home Assistant te demande :

Champ	Description
Adresse IP / Host	Adresse du module ALLIN (ex: 192.168.1.50)
Nom d’utilisateur	Identifiant de connexion (si protection activée)
Mot de passe	Mot de passe d’accès à l’API locale

Ensuite l’intégration :

Vérifie la connexion

Valide les identifiants

Découvre les relais

Crée automatiquement les entités

Entités créées

Pour un contrôleur ALLIN I/O 8, Home Assistant crée :

switch.relay_1
switch.relay_2
...
switch.relay_8


Chaque relais expose :

is_on (état)

turn_on()

turn_off()

Attributs propres à l’appareil

Structure de l’intégration
custom_components/allin_io_8/
│
├── __init__.py          → Initialisation / coordinator / hub
├── config_flow.py       → Configuration UI
├── switch.py            → Entités relais
├── const.py             → Constantes
├── manifest.json        → Déclaration HA
├── strings.json         → chaînes génériques HA
└── translations/
    ├── en.json          → Traductions anglaises
    └── fr.json          → Traductions françaises

Dépannage
Impossible de se connecter

Vérifier que l’adresse IP est correcte

Vérifier que l’interface web du module ALLIN répond

Tester depuis un navigateur :

http://<adresse_ip>

Mauvais identifiants

Le message "Invalid authentication" apparaît si l’API refuse la connexion.
→ Vérifier username / password dans l’interface du module.

Les relais ne mettent pas à jour leur état

Vérifier que la librairie interne renvoie bien state ou is_on

Envoyer un exemple d’état si besoin pour adapter switch.py

Tests & Validation

L’intégration a été pensée pour fonctionner dans les environnements :

Home Assistant OS

Home Assistant Core

Containers Docker

Environnements offline

Licence

MIT – libre pour un usage personnel ou commercial.

Contributions

Contributions, pull requests et améliorations bienvenues !
Tu peux proposer :

UI pour renommer les relais

Support avancé (timers, impulsions…)

Un mode diagnostic

Support d’autres cartes ALLIN
