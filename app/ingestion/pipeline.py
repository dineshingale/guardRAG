from typing import List, Dict
from app.ingestion.chunking import SemanticChunker

class IngestionPipeline:
    def __init__(self):
        self.chunker = SemanticChunker()
        self.knowledge_base: List[Dict] = []
        self._seed_default_knowledge()

    def _seed_default_knowledge(self):
        docs = [
            {
                "doc_id": "sec_policy_01",
                "text": "Aegis Sentinel Security Framework mandates zero-trust access, strict PII redaction, and deterministic fallback handling across all LLM pipeline nodes. Access keys must be rotated every 90 days."
            },
            {
                "doc_id": "rag_arch_02",
                "text": "Hybrid Retrieval combines BM25 keyword matching with dense vector similarity scores using Reciprocal Rank Fusion (RRF). RRF constant k is typically set to 60 to balance exact term match and semantic intent."
            },
            {
                "doc_id": "eval_metrics_03",
                "text": "RAG Evaluation measures Context Recall, Context Precision, and Answer Faithfulness using standard gold test sets to ensure zero hallucination drift."
            }
        ]
        for d in docs:
            self.ingest_document(d["doc_id"], d["text"])

    def ingest_document(self, doc_id: str, content: str) -> List[Dict]:
        chunks = self.chunker.create_chunks(content, doc_id)
        self.knowledge_base.extend(chunks)
        return chunks

    def get_all_chunks(self) -> List[Dict]:
        return self.knowledge_base
