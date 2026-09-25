"""
QnA Module for EduGenie
Implements question answering using Google Gemini.
"""
from main import answer_question

def answer_question_with_gemini(question: str) -> str:
    return answer_question(question)

__all__ = ["answer_question_with_gemini", "answer_question"]
