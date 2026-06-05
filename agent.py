from __future__ import annotations

from dotenv import load_dotenv
import os
import re
import warnings
from typing import Any, Dict, List, Sequence

warnings.filterwarnings(
    "ignore",
    message=r".*duckduckgo_search.*renamed to `ddgs`.*",
    category=RuntimeWarning,
)

from ddgs import DDGS
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = (
    "You are STUDY BUDDY, a smart helpful assistant. Answer any question on any topic — "
    "technology, science, health, career, mental health, general knowledge, and everything else. "
    "Understand short forms and abbreviations in context. "
    "Give clear, helpful answers."
)

GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MODEL = GROQ_MODEL
MAX_HISTORY_MESSAGES = 12

abbreviations = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "ds": "data science",
    "cv": "computer vision",
    "nn": "neural network",
    "db": "database",
    "os": "operating system",
    "oop": "object oriented programming",
    "api": "application programming interface",
    "ui": "user interface",
    "ux": "user experience",
    "js": "javascript",
    "py": "python",
    "sql": "structured query language",
}

ABBREVIATION_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, abbreviations.keys()), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def expand_abbreviations(text: str) -> str:
    if not text:
        return text

    def replace(match: re.Match[str]) -> str:
        return abbreviations[match.group(0).lower()]

    return ABBREVIATION_PATTERN.sub(replace, text)


def _normalize_history(messages: Sequence[Any] | None) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for message in (messages or [])[-MAX_HISTORY_MESSAGES:]:
        if isinstance(message, dict):
            role = str(message.get("role", "")).strip()
            content = str(message.get("content", "")).strip()
        elif isinstance(message, (tuple, list)) and len(message) >= 2:
            role = str(message[0]).strip()
            content = str(message[1]).strip()
        else:
            continue

        if role not in {"user", "assistant", "system"} or not content:
            continue

        if role == "user":
            content = expand_abbreviations(content)

        normalized.append({"role": role, "content": content})

    return normalized


def _build_messages(question: str, history: Sequence[Any] | None) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_normalize_history(history))
    messages.append({"role": "user", "content": expand_abbreviations(question)})
    return messages


def _extract_groq_text(response: Any) -> str:
    if not getattr(response, "choices", None):
        return ""

    message = response.choices[0].message
    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: List[str] = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text", "")))
            else:
                text_parts.append(str(getattr(item, "text", item)))
        return "".join(text_parts).strip()

    return str(content).strip()


def _search_duckduckgo(question: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(question, max_results=3))

        if not results:
            return ""

        body_texts: List[str] = []
        for result in results[:2]:
            title = str(result.get("title", "")).strip()
            body = str(result.get("body", "")).strip()
            combined = " ".join(part for part in [title, body] if part).strip()
            if combined:
                body_texts.append(combined)

        if not body_texts:
            return ""

        cleaned_question = question.strip().rstrip("?")
        answer_parts = [
            f"For {cleaned_question.lower()}, here’s a direct answer based on recent web information:",
            "",
            body_texts[0],
        ]
        if len(body_texts) > 1:
            answer_parts.extend(["", body_texts[1]])

        answer_parts.extend(
            [
                "",
                "In short: use the points above as the most relevant current guidance.",
            ]
        )
        return "\n".join(answer_parts).strip()
    except Exception as e:
        print(f"DDG ERROR: {e}")
        return "Sorry, I could not find an answer right now."


def get_response(
    question: str,
    history: Sequence[Any] | None = None,
    model: str = GROQ_MODEL,
    provider: str | None = None,
    style: str | None = None,
    top_k: int | None = None,
) -> str:
    del provider, style, top_k

    cleaned_question = (question or "").strip()
    if not cleaned_question:
        return "Sorry, could not find an answer. Try again."

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key.lower() == "your_key_here":
        return "API key not found. Check your .env file."

    messages = _build_messages(cleaned_question, history)
    resolved_model = model.strip() if model and model.strip() else GROQ_MODEL

    try:
        response = client.chat.completions.create(
            model=resolved_model,
            messages=messages,
        )
        answer = _extract_groq_text(response)
        if answer:
            return answer
        raise RuntimeError("Groq returned an empty response.")
    except Exception:
        try:
            search_summary = _search_duckduckgo(cleaned_question)
            if search_summary:
                return search_summary
        except Exception:
            pass
        return "Sorry, could not find an answer. Try again."


def generate_answer(
    question: str,
    history: Sequence[Any] | None = None,
    provider: str = "groq",
    model: str = GROQ_MODEL,
    style: str = "balanced",
    top_k: int = 4,
) -> Dict[str, Any]:
    answer = get_response(
        question=question,
        history=history,
        model=model,
        provider=provider,
        style=style,
        top_k=top_k,
    )
    return {
        "answer": answer,
        "route": "groq" if answer != "API key not found. Check your .env file." else "error",
        "sources": [],
        "context": "",
        "model": model,
        "provider": "groq",
    }


class StudyBuddyApp:
    def invoke(self, payload: Dict[str, Any], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
        del config

        settings = payload.get("settings", {})
        return generate_answer(
            question=str(payload.get("question", "")),
            history=payload.get("messages", []),
            provider=str(settings.get("provider", "groq")),
            model=str(settings.get("model", GROQ_MODEL)),
            style=str(settings.get("style", "balanced")),
            top_k=int(settings.get("top_k", 4)),
        )


app = StudyBuddyApp()
