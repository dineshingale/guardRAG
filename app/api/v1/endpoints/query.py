from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.api.dependencies import get_ingestion_pipeline, get_input_guardrail, get_output_guardrail
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str = Field(..., example="What are the security access key rotation requirements?")
    top_k: Optional[int] = Field(default=3, ge=1, le=10)

class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    rerank_score: float

class QueryResponse(BaseModel):
    query: str
    sanitized_query: str
    answer: str
    faithfulness_score: float
    retrieved_chunks: List[RetrievedChunk]
    violations: List[str]

@router.post("/query", response_model=QueryResponse, summary="Execute Guardrailed RAG Pipeline")
async def execute_rag_query(
    payload: QueryRequest,
    pipeline = Depends(get_ingestion_pipeline),
    input_guard = Depends(get_input_guardrail),
    output_guard = Depends(get_output_guardrail)
):
    # 1. Input Guardrail Verification & Sanitization
    is_valid, sanitized_q, violations = input_guard.validate_and_sanitize(payload.query)
    if not is_valid:
        return QueryResponse(
            query=payload.query,
            sanitized_query=sanitized_q,
            answer="Request rejected due to security policy violations.",
            faithfulness_score=0.0,
            retrieved_chunks=[],
            violations=violations
        )

    # 2. Hybrid Retrieval & Reranking
    all_chunks = pipeline.get_all_chunks()
    retriever = HybridRetriever(all_chunks)
    candidates = retriever.retrieve(sanitized_q, top_k=payload.top_k)
    
    reranker = CrossEncoderReranker()
    final_chunks = reranker.rerank(sanitized_q, candidates)

    # 3. LLM Generation
    contexts = [c["text"] for c in final_chunks]
    context_str = "\n---\n".join(contexts)
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "mock-key":
        raw_answer = f"Based on retrieved documentation: {contexts[0] if contexts else 'No relevant context found.'}"
    else:
        llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY, temperature=0)
        prompt = f"Answer the user query strictly using the provided context.\nContext:\n{context_str}\n\nQuery: {sanitized_q}"
        res = await llm.ainvoke([SystemMessage(content="You are an Enterprise RAG Assistant."), HumanMessage(content=prompt)])
        raw_answer = res.content

    # 4. Output Guardrail & Groundedness Verification
    is_safe, final_answer, faith_score = output_guard.verify_output(raw_answer, contexts)

    return QueryResponse(
        query=payload.query,
        sanitized_query=sanitized_q,
        answer=final_answer,
        faithfulness_score=faith_score,
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id=c["chunk_id"],
                doc_id=c["doc_id"],
                text=c["text"],
                rerank_score=c["rerank_score"]
            ) for c in final_chunks
        ],
        violations=[]
    )
