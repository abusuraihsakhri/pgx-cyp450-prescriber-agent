"""
Deterministic demonstration responder. No external language-model services are invoked.
"""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Pgx Cyp450 Prescriber Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Demo Responder]: Query received: '{prompt[:60]}...'. No clinical validation or pharmacogenomic guidance was performed."


class LLMFactory:
    """Return a deterministic mock for all providers; no remote provider is connected."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Pgx Cyp450 Prescriber Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        elif prov in ["ollama", "local"]:
            return MockLLM(system_name)
        elif prov in ["claude", "anthropic"]:
            return MockLLM(system_name)
        elif prov in ["openai", "gpt4"]:
            return MockLLM(system_name)
        return MockLLM(system_name)
