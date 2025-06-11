from pydantic import BaseModel
from typing import List, Optional


class QuestionRequest(BaseModel):
    question: str
    character: str


class QuestionResponse(BaseModel):
    question: str
    character: str
    response: str
    context_snippets: List[str]
    confidence_score: float
    processing_time: float


class CharacterTrait(BaseModel):
    trait: str
    score: float
    evidence: List[str]


class Character(BaseModel):
    name: str
    traits: List[CharacterTrait]
    total_mentions: int
