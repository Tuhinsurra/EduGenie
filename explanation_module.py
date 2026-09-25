"""
Explanation Module for EduGenie
Implements concept explanation using LaMini-Flan-T5 (local) or Google Gemini (cloud fallback).
"""
from app.services.explanation_module import explain_concept

def explain_topic(topic: str) -> str:
    return explain_concept(topic)

__all__ = ["explain_topic"]
