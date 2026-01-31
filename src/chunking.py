import os
import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ChunkingConfig:
    max_chunk_size: int = 1500
    min_chunk_size: int = 100
    overlap_size: int = 200
    max_header_level: int = 3


class ChunkingStats:
    
    def __init__(self):
        self.total_chunks = 0
        self.total_chars = 0
        self.chunk_sizes = []
        self.files_processed = 0
    
    def add_chunk(self, size: int):
        self.total_chunks += 1
        self.total_chars += size
        self.chunk_sizes.append(size)
    
    def get_summary(self) -> Dict:
        if not self.chunk_sizes:
            return {}
        
        return {
            "total_chunks": self.total_chunks,
            "total_chars": self.total_chars,
            "avg_chunk_size": int(self.total_chars / self.total_chunks),
            "min_chunk_size": min(self.chunk_sizes),
            "max_chunk_size": max(self.chunk_sizes),
            "files_processed": self.files_processed
        }
    
    def print_summary(self):
        summary = self.get_summary()
        if not summary:
            print("Aucune statistique disponible")
            return
        
        print(f"\n📊 Statistiques du chunking:")
        print(f"  • Fichiers traités : {summary['files_processed']}")
        print(f"  • Total chunks : {summary['total_chunks']}")
        print(f"  • Total caractères : {summary['total_chars']:,}")
        print(f"  • Taille moyenne : {summary['avg_chunk_size']} chars")
        print(f"  • Taille min : {summary['min_chunk_size']} chars")
        print(f"  • Taille max : {summary['max_chunk_size']} chars")


def load_markdown_files(data_dir: str = "data") -> List[Dict]:
    documents = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"⚠ Le dossier {data_dir} n'existe pas.")
        return documents
    
    md_files = list(data_path.glob("*.md"))
    if not md_files:
        print(f"⚠ Aucun fichier .md trouvé dans {data_dir}")
        return documents
    
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "filename": file_path.name,
                    "source": file_path.stem,
                    "content": content,
                    "path": str(file_path)
                })
                print(f"✓ Chargé : {file_path.name} ({len(content):,} chars)")
        except Exception as e:
            print(f"✗ Erreur lors du chargement de {file_path.name}: {e}")
    
    return documents


def chunk_by_headers(
    document: Dict, 
    config: ChunkingConfig = None,
    stats: ChunkingStats = None
) -> List[Dict]:
    if config is None:
        config = ChunkingConfig()
    
    content = document["content"]
    source = document["source"]
    
    header_pattern = rf'^(#{{{1},{config.max_header_level}}})\s+(.+)$'
    
    chunks = []
    current_chunk = ""
    current_header = source
    current_header_level = 0
    previous_chunk_end = ""
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        header_match = re.match(header_pattern, line)
        
        if header_match:
            if current_chunk.strip() and len(current_chunk.strip()) >= config.min_chunk_size:
                chunk_content = current_chunk.strip()
                
                if previous_chunk_end and chunks:
                    chunk_content = previous_chunk_end + "\n\n" + chunk_content
                
                chunks.append({
                    "content": chunk_content,
                    "source": source,
                    "header": current_header,
                    "header_level": current_header_level,
                    "size": len(chunk_content)
                })
                
                if stats:
                    stats.add_chunk(len(chunk_content))
                
                overlap_start = max(0, len(current_chunk) - config.overlap_size)
                previous_chunk_end = current_chunk[overlap_start:].strip()
            
            current_header_level = len(header_match.group(1))
            current_header = header_match.group(2)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
            
            if len(current_chunk) > config.max_chunk_size:
                chunk_content = current_chunk.strip()
                
                if previous_chunk_end and chunks:
                    chunk_content = previous_chunk_end + "\n\n" + chunk_content
                
                chunks.append({
                    "content": chunk_content,
                    "source": source,
                    "header": current_header,
                    "header_level": current_header_level,
                    "size": len(chunk_content)
                })
                
                if stats:
                    stats.add_chunk(len(chunk_content))
                
                overlap_start = max(0, len(current_chunk) - config.overlap_size)
                previous_chunk_end = current_chunk[overlap_start:].strip()
                current_chunk = ""
    
    if current_chunk.strip() and len(current_chunk.strip()) >= config.min_chunk_size:
        chunk_content = current_chunk.strip()
        
        if previous_chunk_end and chunks:
            chunk_content = previous_chunk_end + "\n\n" + chunk_content
        
        chunks.append({
            "content": chunk_content,
            "source": source,
            "header": current_header,
            "header_level": current_header_level,
            "size": len(chunk_content)
        })
        
        if stats:
            stats.add_chunk(len(chunk_content))
    
    return chunks


def process_all_documents(
    data_dir: str = "data",
    config: ChunkingConfig = None,
    verbose: bool = True
) -> tuple[List[Dict], ChunkingStats]:
    if config is None:
        config = ChunkingConfig()
    
    stats = ChunkingStats()
    documents = load_markdown_files(data_dir)
    stats.files_processed = len(documents)
    
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_by_headers(doc, config, stats)
        all_chunks.extend(chunks)
        
        if verbose:
            print(f"  → {len(chunks)} chunks créés pour {doc['filename']}")
    
    if verbose:
        print(f"\n✓ Total : {len(all_chunks)} chunks créés")
        stats.print_summary()
    
    return all_chunks, stats


if __name__ == "__main__":
    config = ChunkingConfig(
        max_chunk_size=1500,
        min_chunk_size=100,
        overlap_size=200,
        max_header_level=3
    )
    
    chunks, stats = process_all_documents(config=config)
    
    print("\n" + "="*50)
    print("Exemples de chunks créés:")
    print("="*50)
    
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk['source']}")
        print(f"Section: {chunk['header']} (niveau {chunk['header_level']})")
        print(f"Taille: {chunk['size']} chars")
        print(f"Contenu: {chunk['content'][:200]}...")
