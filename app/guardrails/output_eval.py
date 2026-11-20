from typing import Tuple, List
import re

def re_words(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r'\b\w{4,}\b', text)]

class OutputGuardrail:
    def __init__(self):
        self.banned_phrases = [
            "internal system prompt",
            "unverified medical diagnostic",
            "financial trade advice guarantee"
        ]

    def verify_output(self, response_text: str, source_contexts: List[str]) -> Tuple[bool, str, float]:
        lowered = response_text.lower()
        for phrase in self.banned_phrases:
            if phrase in lowered:
                return False, "Security Policy Triggered: Output contained restricted content.", 0.0

        if not source_contexts:
            return True, response_text, 0.5

        response_words = set(re_words(response_text))
        if not response_words:
            return True, response_text, 1.0

        context_words = set()
        for ctx in source_contexts:
            context_words.update(re_words(ctx))

        overlap = response_words.intersection(context_words)
        faithfulness_score = round(len(overlap) / len(response_words), 2)

        if faithfulness_score < 0.25:
            safe_fallback = f"{response_text}\n\n*[Notice: Response grounded status verified at low confidence ({faithfulness_score})]*"
            return True, safe_fallback, faithfulness_score

        return True, response_text, min(faithfulness_score, 1.0)
