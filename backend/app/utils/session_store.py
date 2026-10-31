"""
session_store.py
Simple file-based session storage for interaction logging.
Phase 2 will replace with MongoDB using the existing MONGO_URI from .env
"""
import json
import os
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

SESSION_DIR = Path(__file__).parent.parent.parent / "scratch" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _get_session_path(session_id: str) -> Path:
    """Return path for session file, sanitizing the ID to prevent path traversal."""
    safe_id = "".join(c for c in session_id if c.isalnum() or c == "-")[:64]
    return SESSION_DIR / f"{safe_id}.json"


def log_interaction(
    session_id: str,
    subject: str,
    topic: str,
    question_text: str,
    marks_available: int,
    marks_obtained: Optional[int],
    mode: str,
    examiner_band: Optional[str] = None,
) -> dict:
    """Log a single student interaction to the session file."""
    interaction = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "subject": subject,
        "topic": topic,
        "question_text": question_text[:500],  # Truncate for storage efficiency
        "marks_available": marks_available,
        "marks_obtained": marks_obtained,
        "mode": mode,
        "examiner_band": examiner_band,
        "timestamp": datetime.now().isoformat(),
    }

    path = _get_session_path(session_id)

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"session_id": session_id, "interactions": [], "created_at": datetime.now().isoformat()}

    data["interactions"].append(interaction)
    data["last_active"] = datetime.now().isoformat()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return interaction


def get_session_interactions(session_id: str) -> list:
    """Retrieve all interactions for a session."""
    path = _get_session_path(session_id)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("interactions", [])
    except (json.JSONDecodeError, OSError):
        return []


def get_session_summary(session_id: str) -> dict:
    """Return a high-level summary of the session."""
    interactions = get_session_interactions(session_id)
    if not interactions:
        return {"total": 0, "subjects": [], "topics": []}

    subjects = list({ix.get("subject", "unknown") for ix in interactions})
    topics = list({ix.get("topic", "general") for ix in interactions})
    scored = [ix for ix in interactions if ix.get("marks_obtained") is not None]

    return {
        "total": len(interactions),
        "scored": len(scored),
        "subjects": subjects,
        "topics": topics,
        "first_interaction": interactions[0].get("timestamp"),
        "last_interaction": interactions[-1].get("timestamp"),
    }

