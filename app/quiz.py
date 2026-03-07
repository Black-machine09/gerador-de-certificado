from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


def normalize_text(value: object) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_partner(value: object) -> str:
    return normalize_text(value).replace(" ", "")


ACCEPTED_ORADOR = {"robson paniaco", "robson paniago"}
ACCEPTED_MODERADOR = {"helio emanuel"}
ACCEPTED_PARTNERS = {"ti360", "nexmind", "linkup"}
ACCEPTED_TEMA = {
    "como ter mentalidade de sucesso na vida academica e profissional",
    "como ter mentalidade de sucesso na vida pessoal e profissional",
}


@dataclass(frozen=True)
class QuizValidation:
    ok: bool
    field: str | None = None


def validate_quiz_answers(answers: dict) -> QuizValidation:
    orador = normalize_text(answers.get("orador"))
    moderador = normalize_text(answers.get("moderador"))
    tema = normalize_text(answers.get("tema"))
    parceiros_in = answers.get("parceiros") or []

    parceiros = {normalize_partner(p) for p in parceiros_in if str(p or "").strip()}

    if orador not in ACCEPTED_ORADOR:
        return QuizValidation(ok=False, field="orador")
    if moderador not in ACCEPTED_MODERADOR:
        return QuizValidation(ok=False, field="moderador")
    if tema not in ACCEPTED_TEMA:
        return QuizValidation(ok=False, field="tema")

    if parceiros != ACCEPTED_PARTNERS:
        return QuizValidation(ok=False, field="parceiros")

    return QuizValidation(ok=True)

