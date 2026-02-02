# 🚀 Portfolio LLM - Portfolio Interactif Intelligent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://eferouxportfolio.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents-green?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)

> Portfolio professionnel propulsé par l'IA utilisant un système RAG pour répondre aux questions sur mon parcours, mes compétences et mes projets.

## 🌟 Liens

- **🔗 [Application en ligne](https://eferouxportfolio.streamlit.app/)**
- **📦 [Code source](https://github.com/elliotfx/PortfolioLLM)**

---

## 🎯 C'est quoi ?

Un portfolio interactif qui utilise l'intelligence artificielle pour créer une expérience conversationnelle. Les visiteurs peuvent poser des questions naturelles et recevoir des réponses personnalisées sur mon profil au lieu de lire un CV statique.

## ✨ Fonctionnalités

- 💬 **Chat interactif** - Interface conversationnelle pour explorer le portfolio
- 🔍 **Recherche sémantique** - RAG avec Upstash Vector pour des réponses contextuelles
- 🤖 **Agent IA** - Propulsé par OpenAI Agents et GPT-4.1-nano
- 📚 **Base de connaissances** - Documents en Markdown (profil, formations, expériences, projets)
- 🎨 **Design moderne** - Interface Streamlit avec thème sombre

## 🛠️ Technologies

- **Python 3.12+** - Langage de programmation
- **Streamlit 1.52.2** - Framework d'application web
- **OpenAI Agents 0.6.5** - Framework d'agents IA
- **Upstash Vector 0.8.0** - Base de données vectorielle
- **GPT-4.1-nano** - Modèle de langage

---

## 💻 Installation

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/elliotfx/PortfolioLLM.git
cd PortfolioLLM
```

### 2️⃣ Créer l'environnement virtuel

**Windows :**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac :**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY="sk-proj-..."
UPSTASH_VECTOR_REST_URL="https://your-endpoint.upstash.io"
UPSTASH_VECTOR_REST_TOKEN="your-token-here"
```

---

## 🚀 Utilisation

### Indexer les documents

```bash
python -m src.indexing
```

### Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible sur **http://localhost:8501** 🌐

### Exemples de questions

- "Quel est ton parcours académique ?"
- "Quelles sont tes compétences en data science ?"
- "Parle-moi de tes projets"
- "Quelle est ton expérience professionnelle ?"

---

## 📁 Structure du Projet

```
LLMPortfolio/
├── data/                    # Documents Markdown (profil, formations, expériences, projets)
├── src/                     # Code source
│   ├── chunking.py         # Découpage des documents
│   ├── indexing.py         # Indexation Upstash Vector
│   ├── tools.py            # Tool RAG pour la recherche
│   └── agent.py            # Configuration de l'agent
├── app.py                  # Application Streamlit
├── requirements.txt        # Dépendances
└── README.md
```

---

## 🎨 Personnalisation

Pour adapter le portfolio à votre profil :

1. **Modifier les fichiers Markdown** dans le dossier `data/` :
   - `profil.md` - Présentation et contact
   - `formation.md` - Parcours académique
   - `experiences.md` - Expériences professionnelles
   - `projets.md` - Projets réalisés
   - `competences.md` - Compétences techniques
   - `interets.md` - Centres d'intérêt

2. **Réindexer les documents** :
   ```bash
   python -m src.indexing
   ```

---

## 📄 Licence

Projet universitaire et personnel.

---

<p align="center">
  <strong>Fait avec ❤️ et 🤖</strong>
</p>