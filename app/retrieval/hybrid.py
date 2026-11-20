from typing import List, Dict
import math

class HybridRetriever:
    def __init__(self, knowledge_chunks: List[Dict]):
        self.chunks = knowledge_chunks

    def _bm25_score(self, query: str, text: str) -> float:
        q_words = set(query.lower().split())
        t_words = text.lower().split()
        if not t_words:
            return 0.0
        score = 0.0
        for word in q_words:
            count = t_words.count(word)
            if count > 0:
                score += (count / len(t_words)) * math.log(1 + len(t_words))
        return score

    def _semantic_score(self, query: str, text: str) -> float:
        q_set = set(query.lower())
        t_set = set(text.lower())
        if not t_set:
            return 0.0
        return len(q_set.intersection(t_set)) / len(q_set.union(t_set))

    def retrieve(self, query: str, top_k: int = 3, rrf_k: int = 60) -> List[Dict]:
        scored_chunks = []
        
        for idx, chunk in enumerate(self.chunks):
            bm25 = self._bm25_score(query, chunk["text"])
            semantic = self._semantic_score(query, chunk["text"])
            
            rrf_score = (1.0 / (rrf_k + (1 / (bm25 + 0.001)))) + (1.0 / (rrf_k + (1 / (semantic + 0.001))))
            
            scored_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "rrf_score": round(rrf_score, 4),
                "bm25_score": round(bm25, 4),
                "semantic_score": round(semantic, 4)
            })
            
        scored_chunks.sort(key=lambda x: x["rrf_score"], reverse=True)
        return scored_chunks[:top_k]
