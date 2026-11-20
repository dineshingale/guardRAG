import re
from typing import Tuple, List

class InputGuardrail:
    def __init__(self):
        # Regex patterns for basic PII masking
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        
        # Jailbreak / Injection patterns
        self.injection_keywords = [
            "ignore previous instructions",
            "system prompt leak",
            "you are now in developer mode",
            "dan mode",
            "bypass security policies"
        ]

    def validate_and_sanitize(self, text: str) -> Tuple[bool, str, List[str]]:
        violations = []
        lowered = text.lower()
        
        # Check prompt injection
        for kw in self.injection_keywords:
            if kw in lowered:
                violations.append(f"Prompt Injection Detected: '{kw}'")
                
        if violations:
            return False, text, violations
            
        # Mask PII
        sanitized = self.email_pattern.sub("[REDACTED_EMAIL]", text)
        sanitized = self.phone_pattern.sub("[REDACTED_PHONE]", sanitized)
        sanitized = self.ssn_pattern.sub("[REDACTED_SSN]", sanitized)
        
        return True, sanitized, []
