"""
Explanation Module for EduGenie
Implements concept explanation using Google Gemini.
"""
from main import explain_concept

def explain_topic(topic: str) -> str:
    return explain_concept(topic)

__all__ = ["explain_topic", "explain_concept"]
