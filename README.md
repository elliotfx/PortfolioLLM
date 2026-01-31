# 🚀 Portfolio LLM

Portfolio interactif utilisant un agent IA (RAG) pour répondre aux questions sur mon profil professionnel.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52-red?style=flat-square&logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-Agents-green?style=flat-square&logo=openai)

## 🎯 Fonctionnalités

- 💬 **Chat interactif** - Interface conversationnelle pour explorer le portfolio
- 🔍 **Recherche intelligente (RAG)** - Retrieval-Augmented Generation avec Upstash Vector
- 🤖 **Agent IA** - Propulsé par OpenAI GPT-4.1-nano
- 🎨 **Design moderne** - Interface Streamlit avec thème sombre

## 📁 Structure du projet

```
LLMPortfolio/
├── data/                    # Fichiers Markdown du profil
│   ├── profil.md
│   ├── formation.md
│   ├── experiences.md
│   ├── projets.md
│   ├── competences.md
│   └── interets.md
├── src/                     # Code source
│   ├── chunking.py          # Découpage des documents
│   ├── indexing.py          # Indexation Upstash
│   ├── tools.py             # Tool de recherche RAG
│   └── agent.py             # Configuration de l'agent
├── tests/                   # Tests automatisés
├── app.py                   # Application Streamlit
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/elliotfx/PortfolioLLM.git
cd PortfolioLLM
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY="votre-clé-openai"
UPSTASH_VECTOR_REST_URL="votre-url-upstash"
UPSTASH_VECTOR_REST_TOKEN="votre-token-upstash"
```

### 5. Vérifier la configuration

```bash
pytest -s
```

## 🚀 Utilisation

### Indexer les documents

Avant de lancer l'application, indexez vos documents dans Upstash :

```bash
python -m src.indexing
```

### Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📝 Personnalisation

Pour personnaliser le portfolio, modifiez les fichiers Markdown dans le dossier `data/` :

- **profil.md** - Présentation et contact
- **formation.md** - Parcours académique
- **experiences.md** - Stages et emplois
- **projets.md** - Projets réalisés
- **competences.md** - Compétences techniques
- **interets.md** - Centres d'intérêt

Après modification, réindexez les documents :

```bash
python -m src.indexing
```

## 🌐 Déploiement

Pour déployer sur Streamlit Cloud :

1. Push le code sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repository
4. Configurer les secrets (clés API) dans les paramètres

## 🔧 Technologies utilisées

| Technologie | Description |
|-------------|-------------|
| **Python 3.12+** | Langage de programmation |
| **Streamlit** | Framework d'application web |
| **OpenAI Agents** | Framework d'agents IA |
| **Upstash Vector** | Base de données vectorielle |
| **GPT-4.1-nano** | Modèle de langage |

## 📄 Licence

Ce projet est réalisé dans le cadre d'un projet universitaire.

---

<p align="center">
  Fait avec ❤️ et beaucoup de ☕
</p>