"""Validate a curated evidence packet and produce review signals, not a verdict."""

from __future__ import annotations

from datetime import date
from itertools import combinations
from typing import Any, Protocol
from urllib.parse import urlsplit, urlunsplit

MAX_ITEMS = 40
MAX_PAIN_ITEMS = 20
OVERLAP_THRESHOLD = 0.70
KINDS = {"pain", "workaround", "counter", "competitor", "attention"}
VOICES = {"first_hand", "reported", "product_claim"}


class Entailer(Protocol):
    def entailment(self, premise: str, hypothesis: str) -> float: ...


def _required_text(value: Any, field: str, maximum: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    cleaned = value.strip()
    if len(cleaned) > maximum:
        raise ValueError(f"{field} exceeds {maximum} characters")
    return cleaned


def _web_url(value: Any, field: str) -> str:
    url = _required_text(value, field, 2000)
    parts = urlsplit(url)
    if parts.scheme not in {"https", "http"} or not parts.netloc or parts.username or parts.password:
        raise ValueError(f"{field} must be a public http(s) URL without credentials")
    return url


def _canonical_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), host, path, "", ""))


def validate_packet(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")
    if packet.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    idea = packet.get("idea")
    if not isinstance(idea, dict):
        raise ValueError("idea must be an object")
    normalized_idea = {
        "name": _required_text(idea.get("name"), "idea.name", 200),
        "target_user": _required_text(idea.get("target_user"), "idea.target_user", 500),
        "problem": _required_text(idea.get("problem"), "idea.problem", 1000),
    }
    raw_items = packet.get("evidence")
    if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= MAX_ITEMS:
        raise ValueError(f"evidence must contain 1–{MAX_ITEMS} items")
    seen_ids: set[str] = set()
    items: list[dict[str, Any]] = []
    for position, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"evidence[{position}] must be an object")
        item_id = _required_text(raw.get("id"), f"evidence[{position}].id", 100)
        if item_id in seen_ids:
            raise ValueError(f"duplicate evidence id: {item_id}")
        seen_ids.add(item_id)
        kind = raw.get("kind")
        voice = raw.get("voice")
        if kind not in KINDS or voice not in VOICES:
            raise ValueError(f"evidence[{position}] has invalid kind or voice")
        published = _required_text(raw.get("published_at"), f"evidence[{position}].published_at", 10)
        try:
            published_date = date.fromisoformat(published)
        except ValueError as exc:
            raise ValueError(f"evidence[{position}].published_at must be YYYY-MM-DD") from exc
        if published_date > date.today():
            raise ValueError(f"evidence[{position}].published_at cannot be in the future")
        url = _web_url(raw.get("url"), f"evidence[{position}].url")
        thread_url = _web_url(raw.get("thread_url", url), f"evidence[{position}].thread_url")
        items.append({
            "id": item_id,
            "kind": kind,
            "voice": voice,
            "url": url,
            "thread_url": thread_url,
            "channel": _required_text(raw.get("channel"), f"evidence[{position}].channel", 100).lower(),
            "author": _required_text(raw.get("author"), f"evidence[{position}].author", 150).lower(),
            "published_at": published,
            "claim": _required_text(raw.get("claim"), f"evidence[{position}].claim", 500),
            "observation": _required_text(raw.get("observation"), f"evidence[{position}].observation", 1000),
        })
    return {"schema_version": 1, "idea": normalized_idea, "evidence": items}


def audit(packet: dict[str, Any], model: Entailer | None = None) -> dict[str, Any]:
    normalized = validate_packet(packet)
    items = normalized["evidence"]
    pains = [item for item in items if item["kind"] == "pain" and item["voice"] == "first_hand"]
    if len(pains) > MAX_PAIN_ITEMS:
        raise ValueError(f"at most {MAX_PAIN_ITEMS} first-hand pain items are supported")
    channels = sorted({item["channel"] for item in items})
    first_hand_channels = sorted({item["channel"] for item in pains})
    unique_threads = {_canonical_url(item["thread_url"]) for item in pains}
    unique_voices = {(item["channel"], item["author"]) for item in pains}
    dates = sorted(date.fromisoformat(item["published_at"]) for item in pains)
    span_days = (dates[-1] - dates[0]).days if len(dates) > 1 else 0

    exact_overlap: list[dict[str, str]] = []
    for left, right in combinations(pains, 2):
        reason = None
        if (left["channel"], left["author"]) == (right["channel"], right["author"]):
            reason = "same channel and author"
        elif _canonical_url(left["thread_url"]) == _canonical_url(right["thread_url"]):
            reason = "same discussion thread"
        elif _canonical_url(left["url"]) == _canonical_url(right["url"]):
            reason = "same source URL"
        if reason:
            exact_overlap.append({"left": left["id"], "right": right["id"], "reason": reason})

    semantic_overlap: list[dict[str, Any]] = []
    if len(pains) >= 2:
        if model is None:
            raise ValueError("a real NLI model is required to audit multiple first-hand pain items")
        for left, right in combinations(pains, 2):
            forward = model.entailment(left["claim"], right["claim"])
            reverse = model.entailment(right["claim"], left["claim"])
            if min(forward, reverse) >= OVERLAP_THRESHOLD:
                semantic_overlap.append({
                    "left": left["id"],
                    "right": right["id"],
                    "forward_entailment": round(forward, 4),
                    "reverse_entailment": round(reverse, 4),
                    "interpretation": "possible shared problem; inspect original posts",
                })

    gaps: list[str] = []
    if len(unique_voices) < 3:
        gaps.append("Fewer than three distinct first-hand author/channel identities; aliases are not verified.")
    if len(first_hand_channels) < 2:
        gaps.append("First-hand pain evidence covers fewer than two channel types.")
    if span_days < 7:
        gaps.append("First-hand pain evidence does not span at least one week.")
    if not any(item["kind"] == "counter" for item in items):
        gaps.append("No counter-evidence or satisfied-user experience recorded.")
    if not any(item["kind"] == "competitor" for item in items):
        gaps.append("No direct or adjacent competitor evidence recorded.")
    if not any(item["kind"] == "workaround" for item in items):
        gaps.append("No observed current workaround recorded.")
    gaps.append("Public posts alone cannot establish willingness to pay, retention, or product-market fit; interview or observe real users.")

    return {
        "schema_version": 1,
        "idea": normalized["idea"],
        "counts": {
            "all_records": len(items),
            "first_hand_pain_records": len(pains),
            "distinct_first_hand_identities": len(unique_voices),
            "distinct_first_hand_threads": len(unique_threads),
            "all_channels": channels,
            "first_hand_channels": first_hand_channels,
            "first_hand_span_days": span_days,
        },
        "exact_overlap": exact_overlap,
        "semantic_overlap_review": semantic_overlap,
        "gaps": gaps,
        "records": items,
        "model": "cross-encoder/nli-MiniLM2-L6-H768" if len(pains) >= 2 else "not_needed_for_single_pain_record",
        "warning": "Model signals are not calibrated truth or independent-demand counts. Review original sources.",
    }
