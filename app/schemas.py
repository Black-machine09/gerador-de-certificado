from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class QuizAnswers(BaseModel):
    orador: str
    moderador: str
    parceiros: list[str] = Field(default_factory=list)
    tema: str


class IssueCertificateRequest(BaseModel):
    fullName: str = Field(min_length=3, max_length=80)
    email: EmailStr
    answers: QuizAnswers
