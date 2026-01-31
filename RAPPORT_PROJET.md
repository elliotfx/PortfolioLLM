# RAPPORT DE PROJET
## Portfolio Interactif avec Intelligence Artificielle

**Étudiant** : Elliot FEROUX  
**Formation** : BUT Science des Données - 3ème année  
**Projet** : Portfolio intelligent avec agent conversationnel  
**Date** : Janvier 2026

---

## 1. INTRODUCTION

### 1.1 Problématique et Enjeux

Dans un contexte de recherche d'emploi ou d'alternance, il est crucial de se démarquer. Un CV classique présente des limites : informations statiques, difficultés à mettre en avant toutes ses compétences, et manque d'interactivité.

**La question centrale** : Comment créer un portfolio qui permette aux recruteurs d'obtenir rapidement les informations qu'ils cherchent, tout en offrant une expérience moderne et engageante ?

### 1.2 Solution Proposée

J'ai développé un **portfolio intelligent** qui utilise l'intelligence artificielle pour répondre aux questions des recruteurs de manière conversationnelle. Au lieu de chercher manuellement dans un CV, le recruteur peut simplement demander : *"Quelles sont tes compétences en Python ?"* ou *"Parle-moi de ton alternance"*.

**Technologies choisies** :
- **Streamlit** : Framework Python pour créer rapidement l'interface web
- **OpenAI Agents** : Pour créer l'assistant conversationnel
- **Upstash Vector** : Base de données spécialisée pour stocker les informations
- **Three.js** : Librairie JavaScript pour la visualisation 3D

**Pourquoi ces choix ?**
- Streamlit est simple et rapide à déployer
- OpenAI offre des modèles IA de qualité professionnelle
- Upstash Vector est gratuit pour les petits projets
- Three.js permet des effets visuels impressionnants



## 2. FONCTIONNEMENT DU SYSTÈME RAG

### 2.1 Qu'est-ce qu'un système RAG ?

**RAG** signifie *Retrieval-Augmented Generation* (Génération Augmentée par Récupération). C'est une technique qui permet à une IA de répondre en se basant sur **mes vraies données** plutôt que sur ses connaissances générales.

**Problème sans RAG** : Si je demande à ChatGPT "Où travaille Elliot Feroux ?", il ne peut pas répondre car il ne me connaît pas.

**Solution avec RAG** : Le système va d'abord chercher l'information dans mes documents, puis générer une réponse basée sur ce qu'il a trouvé.

### 2.2 Étape 1 : Préparation des Données (Indexation)

#### 2.2.1 Organisation des Documents

J'ai organisé mes informations dans 5 fichiers Markdown :
- `profil.md` : Qui je suis, mes objectifs
- `experiences.md` : Mon alternance à la Mutuelle de Poitiers
- `formation.md` : Mon parcours BUT Science des Données
- `competences.md` : Mes compétences techniques (Python, SQL, Tableau...)
- `projets.md` : Mes réalisations académiques
- `interets.md` : Centres d'intérêt (notamment arbitrage basketball région)

**Pourquoi Markdown ?** 
- Format texte simple et structuré
- Facile à modifier sans éditeur spécial
- Titres et sous-titres bien définis (utile pour la suite)

#### 2.2.2 Découpage en "Chunks"

**Le problème** : Mes 5 fichiers contiennent beaucoup d'informations (~50 000 caractères au total). C'est trop pour envoyer à l'IA d'un coup.

**La solution** : Découper en petits morceaux appelés "chunks" (morceaux en anglais).

```python
@dataclass
class ChunkingConfig:
    max_chunk_size: int = 1500      # Taille max d'un morceau
    min_chunk_size: int = 100       # Taille min d'un morceau
    overlap_size: int = 200         # Chevauchement entre morceaux
    max_header_level: int = 3       # Découpe jusqu'aux titre ###
```

**Décisions importantes et pourquoi** :

1. **Taille maximale de 1500 caractères** (augmentée de 1000 initialement)
   - *Pourquoi ?* Les morceaux trop petits perdent le contexte
   - *Exemple* : Si un chunk contient juste "Tableau Software" sans expliquer que je l'utilise en alternance, l'information est incomplète
   - 1500 caractères = environ 2-3 paragraphes complets

2. **Taille minimale de 100 caractères**
   - *Pourquoi ?* Éviter les morceaux vides ou trop courts
   - *Exemple* : Un chunk avec juste "## Compétences" n'apporte aucune information utile

3. **Overlap de 200 caractères** (CRUCIAL !)
   - *Qu'est-ce que c'est ?* Les 200 derniers caractères d'un chunk sont répétés au début du chunk suivant
   - *Pourquoi ?* Assurer la continuité du contexte
   
   **Exemple concret** :
   ```
   Chunk 1 : "...en alternance à la Mutuelle de Poitiers Assurances"
   Chunk 2 : "Mutuelle de Poitiers Assurances. Mes missions principales..."
   ```
   Sans overlap, le Chunk 2 perdrait le lien avec l'alternance !

4. **Découpage basé sur les titres Markdown** (# à ###)
   - *Pourquoi ?* Respecter la structure logique du document
   - Au lieu de couper au milieu d'un paragraphe, on coupe au niveau des sections
   
**Résultat** : 39 chunks créés, taille moyenne 1200 caractères

#### 2.2.3 Transformation en Vecteurs (Embeddings)

**Le problème** : L'ordinateur ne comprend pas le texte comme nous. Il faut convertir "Je travaille en alternance" en nombres.

**La solution** : Les *embeddings* (plongements vectoriels)

Chaque chunk est transformé en une suite de 1536 nombres qui représentent le "sens" du texte. C'est un peu comme une empreinte digitale sémantique.

```python
def create_vector_from_chunk(chunk: Dict) -> Vector:
    vector_id = f"{chunk['source']}-{uuid.uuid4().hex[:8]}"
    
    metadata = {
        "source": chunk["source"],           # De quel fichier vient ce chunk
        "section": chunk["header"],          # Quel titre/section
        "content": chunk["content"],         # Le texte complet
        "size": len(chunk["content"]),      # Nombre de caractères
        "indexed_at": datetime.now()         # Quand a-t-il été indexé
    }
    
    return Vector(id=vector_id, data=chunk["content"], metadata=metadata)
```

**Métadonnées ajoutées** :
- `source` : Pour savoir si l'info vient de "experiences" ou "competences"
- `indexed_at` : Pour savoir quand j'ai mis à jour mes données
- `size` : Pour déboguer si des chunks sont trop grands/petits

**Pourquoi ces métadonnées ?**
- Permet de filtrer (ex: "cherche uniquement dans experiences")
- Facilite la maintenance (je sais quels chunks sont anciens)
- Aide au débogage (je peux vérifier les tailles)

#### 2.2.4 Sauvegarde dans la Base Vectorielle

Les 39 vecteurs sont envoyés à Upstash Vector, une base de données spécialisée dans le stockage de vecteurs.

**Optimisation : Envoi par batch**
```python
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + 10]  # Groupes de 10
    
    for attempt in range(3):  # Jusqu'à 3 essais
        try:
            index.upsert(vectors=batch)
            break  # Succès, on passe au batch suivant
        except Exception as e:
            time.sleep(2 * (attempt + 1))  # Attendre 2s, 4s, 6s
```

**Pourquoi par batch de 10 ?**
- Envoyer 39 vecteurs d'un coup pourrait échouer si la connexion coupe
- Par groupes de 10, si un groupe échoue, on peut réessayer sans tout renvoyer

**Pourquoi 3 essais avec délai ?**
- Internet peut avoir des coupures temporaires
- Le délai exponentiel (2s, 4s, 6s) laisse le temps au réseau de se rétablir
- *Résultat* : 100% de réussite sur mes tests

### 2.3 Étape 2 : Répondre aux Questions (Génération)

Quand un recruteur pose une question, voici ce qui se passe :

#### 2.3.1 Recherche Sémantique

1. **La question est transformée en vecteur** (même processus qu'à l'indexation)
   
2. **Recherche des 5 chunks les plus similaires**
   ```python
   results = index.query(data=question, top_k=5)
   ```
   
   *Qu'est-ce que "similaire" ?* Le système calcule la distance mathématique entre le vecteur de la question et les 39 vecteurs stockés. Les 5 plus proches sont sélectionnés.

3. **Exemple concret** :
   - Question : "Quelles technologies utilises-tu en alternance ?"
   - Chunks trouvés : 
     - Chunk de `experiences.md` sur mes outils (Tableau, SQL, Python)
     - Chunk de `competences.md` sur Dremio
     - Chunk sur mes missions de Data Analyst

**Pourquoi top_k=5 ?**
- Moins de 5 : risque de manquer du contexte
- Plus de 5 : trop d'informations inutiles diluent la réponse
- 5 est un bon compromis testé empiriquement

#### 2.3.2 Génération de la Réponse

L'agent IA reçoit les 5 chunks et génère une réponse :

```python
agent = Agent(
    name="Portfolio Assistant",
    instructions=f"""
    Tu es un assistant qui présente Elliot Feroux.
    
    CONTEXTE RÉCUPÉRÉ :
    {chunks_trouvés}
    
    RÈGLES IMPORTANTES :
    1. Base tes réponses UNIQUEMENT sur le contexte ci-dessus
    2. Si l'info n'est pas dans le contexte, dis-le clairement
    3. Sois concis et professionnel
    4. Cite les sources (ex: "D'après son CV...")
    """,
    model="gpt-4o-mini"
)
```

**Pourquoi ces règles strictes ?**
- Sans le "UNIQUEMENT", l'IA pourrait inventer des informations
- "Dis-le clairement" évite les réponses vagues
- Les sources renforcent la crédibilité

**Exemple de réponse** :
```
Question : "Parle-moi de tes activités extra-professionnelles"

Réponse : "En dehors de mes études et de mon alternance, je suis arbitre 
officiel de basketball au niveau région, certifié pour arbitrer en 5x5 
et en 3x3, notamment lors de compétitions universitaires. L'arbitrage 
m'a appris la prise de décision rapide sous pression, la gestion de 
situations conflictuelles et le respect strict des règles - des compétences 
transférables dans mon travail de Data Analyst."
```

### 2.4 Interface Utilisateur

#### Globe 3D Interactif

J'ai intégré un globe terrestre en Three.js qui tourne automatiquement en arrière-plan.

**Pourquoi ?**
- Crée une première impression professionnelle
- Effet "wow" qui marque les recruteurs
- Montre mes compétences en intégration web (Three.js + Streamlit)

#### Bulle de Chat Glassmorphism

Le chat est affiché dans une bulle avec effet de verre flou (glassmorphism).

**Choix de design** :
- Fond semi-transparent avec flou
- Coins très arrondis (32px)
- Ombre portée multicouche
- *Résultat* : Interface moderne et élégante

---

## 3. DÉFIS RENCONTRÉS ET SOLUTIONS

### 3.1 Problème : Chunks trop petits ou trop grands

**Constat initial** : Avec une taille max de 1000 caractères, certains chunks coupaient des phrases importantes.

**Solution** : 
1. Augmentation à 1500 caractères
2. Ajout d'une taille minimum (100 chars)
3. Overlap de 200 chars pour la continuité

**Mesure de l'amélioration** : 
- Avant : 45 chunks, taille moyenne 850 chars
- Après : 39 chunks, taille moyenne 1200 chars
- Meilleure cohérence sémantique

### 3.2 Problème : Perte de Contexte entre Chunks

**Exemple du problème** :
```
Chunk 1 : "...Je travaille sur l'analyse de la sinistralité."
Chunk 2 : "Les tableaux de bord permettent de visualiser..."
```
Le Chunk 2 ne précise pas que c'est *moi* qui crée ces tableaux !

**Solution : Overlap de 200 caractères**
```
Chunk 1 : "...Je travaille sur l'analyse de la sinistralité."
Chunk 2 : "analyse de la sinistralité. Les tableaux de bord que je crée..."
```
Le lien est préservé !

### 3.3 Problème : Gestion des Erreurs Réseau

**Constat** : Lors des tests, parfois l'indexation échouait à cause de coupures réseau momentanées.

**Solution : Retry avec délai exponentiel**
```python
for attempt in range(3):
    try:
        index.upsert(vectors)
        break
    except:
        wait = 2 * (attempt + 1)  # 2s, 4s, 6s
        time.sleep(wait)
```

**Résultat** : Taux de réussite passé de 85% à 100%

---

## 4. RÉSULTATS ET APPRENTISSAGES

### 4.1 Métriques du Projet

**Performance technique** :
- 39 chunks indexés en ~15 secondes
- Temps de réponse moyen : < 2 secondes
- Taux de précision des réponses : Excellent (basé sur tests utilisateurs)

**Qualité du code** :
- 4 modules bien séparés (chunking, indexing, agent, interface)
- Typage de toutes les fonctions
- Statistiques détaillées sur chaque étape
- Gestion d'erreurs robuste

### 4.2 Compétences Développées

**Techniques** :
- Architecture d'un système RAG complet
- Optimisation du chunking pour la recherche sémantique
- Intégration d'APIs (OpenAI, Upstash)
- Développement d'interface web moderne

**Méthodologiques** :
- Tests itératifs et optimisation
- Documentation du code
- Gestion de projet (de l'idée au déploiement)

**Transversales** :
- Recherche et veille technologique
- Résolution de problèmes complexes
- Communication de choix techniques

### 4.3 Points Forts du Projet

✅ **Innovation** : Peu de portfolios utilisent l'IA conversationnelle  
✅ **Qualité** : Code professionnel, bien structuré et documenté  
✅ **Pertinence** : Répond à un vrai besoin (mise en avant de compétences)  
✅ **Technique** : Maîtrise de technologies actuelles (IA, vectorielle)  

---

## 5. CONCLUSION

Ce projet m'a permis de créer un outil innovant tout en consolidant mes compétences en data science et développement. L'approche RAG garantit que les recruteurs obtiennent des informations précises et à jour sur mon profil.

**Perspectives d'évolution** :
- Ajout de documents PDF (CV, certifications)
- Analytics des questions posées
- Personnalisation des réponses selon le type de visiteur

**Ce que j'en retiens** : L'importance de l'itération et de l'optimisation. Les paramètres par défaut (chunk size, overlap) ne sont jamais parfaits du premier coup. Il faut tester, mesurer, et ajuster.

---

**Liens du projet** :
- Repository GitHub : https://github.com/elliotfx/PortfolioLLM
- Application déployée : [URL Streamlit Cloud]
- Documentation technique : README.md
