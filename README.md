# <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Right.png" alt="Magnifying Glass" width="35" /> Open Gemini Deep Research

<div align="center">
  <p>
    <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000&style=flat-square" />
    <img alt="Python" src="https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square&logo=python" />
    <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" />
  </p>

  <h3>Un assistant de recherche open-source surpuissant propulsé par l'IA Gemini de Google</h3>
  <p>Exploration multi-couche approfondie sur n'importe quel sujet</p>
</div>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Rocket.png" alt="Rocket" width="25"/> Fonctionnalités

<table>
  <tr>
    <td>
      <ul>
        <li>🔍 Recherche profonde automatisée à largeur et profondeur ajustables</li>
        <li>🤔 Génération intelligente de questions de suivi</li>
        <li>⚡ Traitement concurrent de multiples requêtes</li>
        <li>📝 Génération de rapports détaillés avec citations</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>🚀 Trois modes de recherche: rapide, équilibré et exhaustif</li>
        <li>📊 Suivi de progression avec visualisation d'arborescence</li>
        <li>🔗 Gestion de sources avec citations en ligne</li>
        <li>🌐 Interface visuelle riche et intuitive</li>
      </ul>
    </td>
  </tr>
</table>



## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="25"/> Prérequis

- Python 3.8+
- Clé API Google Gemini
- Docker (si utilisation du conteneur de développement)
- VS Code avec l'extension Dev Containers (si utilisation du conteneur)

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="25"/> Installation

<details>
<summary><b>Option 1: Utilisation du conteneur de développement (Recommandé)</b></summary>
<br>

1. Ouvrez le projet dans VS Code
2. Quand vous y êtes invité, cliquez sur "Rouvrir dans un conteneur" ou exécutez la commande "Dev Containers: Reopen in Container"
3. Créez un fichier `.env` dans le répertoire racine et ajoutez votre clé API Gemini:
   ```
   GEMINI_KEY=your_api_key_here
   ```
</details>

<details>
<summary><b>Option 2: Installation locale</b></summary>
<br>

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/FeelTheFonk/open-gemini-deep-research
   cd deep_research
   ```

2. Créez et activez un environnement virtuel (recommandé):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

4. Créez un fichier `.env` dans le répertoire racine et ajoutez votre clé API Gemini:
   ```
   GEMINI_KEY=your_api_key_here
   ```
</details>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Joystick.png" alt="Joystick" width="25"/> Utilisation

```bash
python main.py "votre requête de recherche ici"
```

### Arguments optionnels

<table>
  <tr>
    <th>Argument</th>
    <th>Description</th>
    <th>Valeurs</th>
    <th>Défaut</th>
  </tr>
  <tr>
    <td><code>--mode</code></td>
    <td>Mode de recherche</td>
    <td>fast, balanced, comprehensive</td>
    <td>balanced</td>
  </tr>
  <tr>
    <td><code>--num-queries</code></td>
    <td>Nombre de requêtes à générer</td>
    <td>entier</td>
    <td>3</td>
  </tr>
  <tr>
    <td><code>--learnings</code></td>
    <td>Liste d'apprentissages précédents</td>
    <td>liste de chaînes</td>
    <td>[]</td>
  </tr>
</table>

#### Exemple:

```bash
python main.py "Impact de l'intelligence artificielle sur la santé" --mode comprehensive --num-queries 5
```

### Interface graphique

Pour utiliser l'interface utilisateur Rich:

```bash
python ui.py
```

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Clipboard.png" alt="Clipboard" width="25"/> Workflow

Le script va:

1. Analyser votre requête pour déterminer les paramètres optimaux
2. Poser des questions de suivi pour clarification
3. Mener une recherche multi-couche
4. Générer un rapport complet sauvegardé en tant que `final_report.md`
5. Afficher des mises à jour de progression tout au long du processus
6. Générer une visualisation interactive des connaissances (optionnel)

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Card%20File%20Box.png" alt="Structure" width="25"/> Structure du projet

```
deep_research/
├── .github/                   # Configuration GitHub et workflows
├── src/
│   ├── __init__.py
│   └── deep_research.py       # Moteur de recherche principal
├── .env                       # Variables d'environnement (non suivi)
├── .gitignore
├── main.py                    # Point d'entrée CLI
├── ui.py                      # Interface utilisateur Rich
├── README.md
└── requirements.txt           # Dépendances
```

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Light%20Bulb.png" alt="Light Bulb" width="25"/> Fonctionnement

### Modes de recherche

<table>
  <tr>
    <th align="center">⚡ Rapide</th>
    <th align="center">⚖️ Équilibré</th>
    <th align="center">🔍 Exhaustif</th>
  </tr>
  <tr>
    <td>
      • Recherche de surface rapide<br/>
      • Max 3 requêtes concurrentes<br/>
      • Pas de plongée récursive<br/>
      • 2-3 questions par requête<br/>
      • ~1-3 minutes
    </td>
    <td>
      • Profondeur et largeur modérées<br/>
      • Max 7 requêtes concurrentes<br/>
      • Pas de plongée récursive<br/>
      • 3-5 questions par requête<br/>
      • ~3-6 minutes
    </td>
    <td>
      • Recherche détaillée exhaustive<br/>
      • 5 requêtes + plongée récursive<br/>
      • Exploration de relations tertiaires<br/>
      • 5-7 questions avec exploration récursive<br/>
      • ~5-12 minutes
    </td>
  </tr>
</table>

### Processus de recherche

<ol>
  <li><strong>Analyse de requête</strong>
    <ul>
      <li>Évalue la complexité et l'étendue</li>
      <li>Définit la largeur (1-10) et profondeur (1-5)</li>
      <li>Ajuste les paramètres selon le mode</li>
    </ul>
  </li>
  <li><strong>Génération de requêtes</strong>
    <ul>
      <li>Crée des requêtes uniques non-redondantes</li>
      <li>Vérifie la similarité sémantique</li>
      <li>Maintient l'historique pour éviter les doublons</li>
    </ul>
  </li>
  <li><strong>Construction d'arborescence</strong>
    <ul>
      <li>Structure en arbre pour suivre la progression</li>
      <li>Identifiants UUID uniques</li>
      <li>Relations parent-enfant entre requêtes</li>
      <li>Visualisation détaillée via JSON</li>
    </ul>
  </li>
  <li><strong>Recherche approfondie</strong> (Mode exhaustif)
    <ul>
      <li>Stratégie de recherche récursive</li>
      <li>Réduction de largeur aux niveaux profonds</li>
      <li>Déduplication des URLs visitées</li>
    </ul>
  </li>
  <li><strong>Génération de rapport</strong>
    <ul>
      <li>Synthèse narrative cohérente</li>
      <li>Rapport détaillé d'au moins 3000 mots</li>
      <li>Citations en ligne et gestion des sources</li>
      <li>Éléments créatifs (scénarios, analogies)</li>
    </ul>
  </li>
</ol>

### Implémentation technique

L'application utilise l'IA Gemini de Google pour:
- Analyse et génération de requêtes
- Traitement et synthèse de contenu
- Vérification de similarité sémantique
- Génération de rapports

L'arborescence de recherche est implémentée via la classe `ResearchProgress` qui suit:
- Relations entre requêtes (parent-enfant)
- État de complétion des requêtes
- Apprentissages par requête
- Ordre des requêtes
- IDs uniques pour chaque requête

Exemple de structure d'arbre:
```json
{
  "query": "requête racine",
  "id": "uuid-1",
  "status": "completed",
  "depth": 2,
  "learnings": ["apprentissage 1", "apprentissage 2"],
  "sub_queries": [
    {
      "query": "sous-requête 1",
      "id": "uuid-2",
      "status": "completed",
      "depth": 1,
      "learnings": ["apprentissage 3"],
      "sub_queries": [],
      "parent_query": "requête racine"
    }
  ],
  "parent_query": null
}
```

<div align="center">
<p>Explorez les idées. Connectez les connaissances. Découvrez.</p>
</div>