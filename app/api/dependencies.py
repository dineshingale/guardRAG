from functools import lru_cache
from app.ingestion.pipeline import IngestionPipeline
from app.guardrails.input_filter import InputGuardrail
from app.guardrails.output_eval import OutputGuardrail

@lru_cache()
def get_ingestion_pipeline():
    return IngestionPipeline()

@lru_cache()
def get_input_guardrail():
    return InputGuardrail()

@lru_cache()
def get_output_guardrail():
    return OutputGuardrail()
