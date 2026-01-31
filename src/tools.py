"""
Module contenant les Tools pour l'agent IA.
Permet à l'agent d'interroger la base vectorielle Upstash.
"""

import os
from dotenv import load_dotenv
from upstash_vector import Index
from agents import function_tool

load_dotenv(override=True)


def get_index() -> Index:
    """
    Crée et retourne une connexion à l'index Upstash Vector.
    """
    return Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )


@function_tool
def search_portfolio(query: str) -> str:
    """
    Recherche des informations dans le portfolio en utilisant la base vectorielle.
    Utilise cette fonction pour trouver des informations sur le profil, 
    les compétences, les projets, la formation ou les expériences.
    
    Args:
        query: La question ou les mots-clés à rechercher
        
    Returns:
        Les informations pertinentes trouvées dans le portfolio
    """
    index = get_index()
    
    # Recherche hybride (dense + sparse) pour de meilleurs résultats
    results = index.query(
        data=query,
        top_k=5,
        include_metadata=True
    )
    
    if not results:
        return "Aucune information trouvée dans le portfolio pour cette question."
    
    # Formater les résultats
    formatted_results = []
    for result in results:
        if result.metadata:
            source = result.metadata.get("source", "inconnu")
            section = result.metadata.get("section", "")
            content = result.metadata.get("content", "")
            
            formatted_results.append(
                f"[{source.upper()} - {section}]\n{content}"
            )
    
    return "\n\n---\n\n".join(formatted_results)
