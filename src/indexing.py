import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from upstash_vector import Index, Vector

from src.chunking import process_all_documents, ChunkingConfig

load_dotenv(override=True)


@dataclass
class IndexingConfig:
    batch_size: int = 10
    max_retries: int = 3
    retry_delay: int = 2
    clear_first: bool = True


class IndexingStats:
    
    def __init__(self):
        self.start_time = time.time()
        self.total_chunks = 0
        self.successful_chunks = 0
        self.failed_chunks = 0
        self.batches_processed = 0
        self.errors = []
    
    def add_success(self, count: int):
        self.successful_chunks += count
        self.batches_processed += 1
    
    def add_failure(self, count: int, error: str):
        self.failed_chunks += count
        self.errors.append(error)
    
    def get_duration(self) -> float:
        return time.time() - self.start_time
    
    def print_summary(self):
        duration = self.get_duration()
        success_rate = (self.successful_chunks / self.total_chunks * 100) if self.total_chunks > 0 else 0
        
        print(f"\n📊 Statistiques d'indexation:")
        print(f"  • Durée totale : {duration:.2f}s")
        print(f"  • Chunks traités : {self.total_chunks}")
        print(f"  • Chunks réussis : {self.successful_chunks}")
        print(f"  • Chunks échoués : {self.failed_chunks}")
        print(f"  • Taux de réussite : {success_rate:.1f}%")
        print(f"  • Batches traités : {self.batches_processed}")
        
        if self.errors:
            print(f"\n⚠ Erreurs rencontrées ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:3], 1):
                print(f"  {i}. {error}")
            if len(self.errors) > 3:
                print(f"  ... et {len(self.errors) - 3} autre(s)")


def get_index() -> Index:
    url = os.getenv("UPSTASH_VECTOR_REST_URL")
    token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    
    if not url or not token:
        raise ValueError(
            "Les variables UPSTASH_VECTOR_REST_URL et UPSTASH_VECTOR_REST_TOKEN "
            "doivent être définies dans le fichier .env"
        )
    
    return Index(url=url, token=token)


def create_vector_from_chunk(chunk: Dict, include_timestamp: bool = True) -> Vector:
    vector_id = f"{chunk['source']}-{uuid.uuid4().hex[:8]}"
    
    metadata = {
        "source": chunk["source"],
        "section": chunk["header"],
        "content": chunk["content"],
        "size": chunk.get("size", len(chunk["content"])),
        "header_level": chunk.get("header_level", 1)
    }
    
    if include_timestamp:
        metadata["indexed_at"] = datetime.now().isoformat()
    
    return Vector(
        id=vector_id,
        data=chunk["content"],
        metadata=metadata
    )


def index_chunks(
    chunks: List[Dict], 
    config: IndexingConfig = None,
    stats: IndexingStats = None
) -> int:
    if config is None:
        config = IndexingConfig()
    
    if stats is None:
        stats = IndexingStats()
    
    stats.total_chunks = len(chunks)
    
    try:
        index = get_index()
    except Exception as e:
        error_msg = f"Impossible de se connecter à l'index: {e}"
        print(f"✗ {error_msg}")
        if stats:
            stats.add_failure(len(chunks), error_msg)
        return 0
    
    total_indexed = 0
    
    for i in range(0, len(chunks), config.batch_size):
        batch = chunks[i:i + config.batch_size]
        batch_num = i // config.batch_size + 1
        
        for attempt in range(config.max_retries):
            try:
                vectors = [create_vector_from_chunk(chunk) for chunk in batch]
                result = index.upsert(vectors=vectors)
                
                total_indexed += len(batch)
                if stats:
                    stats.add_success(len(batch))
                
                print(f"✓ Batch {batch_num}/{(len(chunks) - 1) // config.batch_size + 1}: "
                      f"{len(batch)} chunks indexés")
                break
                
            except Exception as e:
                if attempt < config.max_retries - 1:
                    wait_time = config.retry_delay * (attempt + 1)
                    print(f"⚠ Batch {batch_num} échoué (tentative {attempt + 1}/{config.max_retries}), "
                          f"nouvelle tentative dans {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    error_msg = f"Batch {batch_num} échoué après {config.max_retries} tentatives: {e}"
                    print(f"✗ {error_msg}")
                    if stats:
                        stats.add_failure(len(batch), error_msg)
    
    return total_indexed


def clear_index() -> bool:
    try:
        index = get_index()
        index.reset()
        print("✓ Index vidé avec succès")
        return True
    except Exception as e:
        print(f"✗ Erreur lors du vidage de l'index: {e}")
        return False


def index_all_documents(
    data_dir: str = "data",
    chunking_config: ChunkingConfig = None,
    indexing_config: IndexingConfig = None,
    verbose: bool = True
) -> tuple[int, IndexingStats]:
    if chunking_config is None:
        chunking_config = ChunkingConfig()
    
    if indexing_config is None:
        indexing_config = IndexingConfig()
    
    indexing_stats = IndexingStats()
    
    print("=" * 50)
    print("INDEXATION DES DOCUMENTS")
    print("=" * 50)
    
    if indexing_config.clear_first:
        print("\n1. Vidage de l'index existant...")
        if not clear_index():
            print("⚠ Impossible de vider l'index, continuation quand même...")
    
    print(f"\n2. Chargement et découpage des documents depuis '{data_dir}'...")
    try:
        chunks, chunking_stats = process_all_documents(
            data_dir, 
            config=chunking_config,
            verbose=verbose
        )
    except Exception as e:
        print(f"✗ Erreur lors du chunking: {e}")
        return 0, indexing_stats
    
    if not chunks:
        print("⚠ Aucun chunk à indexer")
        return 0, indexing_stats
    
    print(f"\n3. Indexation des {len(chunks)} chunks...")
    total = index_chunks(chunks, indexing_config, indexing_stats)
    
    print("\n" + "=" * 50)
    print(f"✓ TERMINÉ : {total}/{len(chunks)} chunks indexés avec succès")
    print("=" * 50)
    
    if verbose:
        indexing_stats.print_summary()
    
    return total, indexing_stats


if __name__ == "__main__":
    chunking_cfg = ChunkingConfig(
        max_chunk_size=1500,
        min_chunk_size=100,
        overlap_size=200,
        max_header_level=3
    )
    
    indexing_cfg = IndexingConfig(
        batch_size=10,
        max_retries=3,
        retry_delay=2,
        clear_first=True
    )
    
    total, stats = index_all_documents(
        chunking_config=chunking_cfg,
        indexing_config=indexing_cfg,
        verbose=True
    )
