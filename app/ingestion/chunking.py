from typing import List, Dict

class SemanticChunker:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, text: str, doc_id: str) -> List[Dict]:
        words = text.split()
        chunks = []
        idx = 0
        chunk_id = 0
        
        while idx < len(words):
            end_idx = min(idx + self.chunk_size, len(words))
            chunk_text = " ".join(words[idx:end_idx])
            
            chunks.append({
                "chunk_id": f"{doc_id}_c{chunk_id}",
                "doc_id": doc_id,
                "text": chunk_text,
                "token_count": len(chunk_text.split())
            })
            
            chunk_id += 1
            idx += (self.chunk_size - self.chunk_overlap)
            if idx >= len(words) - self.chunk_overlap and idx < len(words):
                break
                
        return chunks
