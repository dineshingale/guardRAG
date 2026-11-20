from typing import List, Dict

class CrossEncoderReranker:
    def rerank(self, query: str, candidate_chunks: List[Dict]) -> List[Dict]:
        reranked = []
        q_terms = set(query.lower().split())
        
        for chunk in candidate_chunks:
            text_terms = set(chunk["text"].lower().split())
            exact_overlap = len(q_terms.intersection(text_terms))
            boosted_score = chunk["rrf_score"] + (exact_overlap * 0.05)
            
            item = dict(chunk)
            item["rerank_score"] = round(boosted_score, 4)
            reranked.append(item)
            
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked
