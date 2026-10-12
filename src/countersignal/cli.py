"""Command-line entry point for a curated product evidence packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .core import audit, validate_packet
from .model import LocalNLI


def _safe(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render_markdown(report: dict) -> str:
    idea = report["idea"]
    counts = report["counts"]
    lines = [
        f"# CounterSignal: {_safe(idea['name'])}",
        "",
        f"Target user: {_safe(idea['target_user'])}",
        f"Problem hypothesis: {_safe(idea['problem'])}",
        "",
        "This is an evidence audit, not a build/no-build decision or market estimate.",
        "",
        "## Coverage",
        "",
        f"- Records: {counts['all_records']}; first-hand pain records: {counts['first_hand_pain_records']}",
        f"- Distinct first-hand author/channel identities: {counts['distinct_first_hand_identities']} (aliases not verified)",
        f"- Distinct discussion threads: {counts['distinct_first_hand_threads']}",
        f"- First-hand channels: {', '.join(counts['first_hand_channels']) or 'none'}",
        f"- First-hand time span: {counts['first_hand_span_days']} days",
        "",
        "## Potentially repeated evidence",
        "",
    ]
    if not report["exact_overlap"] and not report["semantic_overlap_review"]:
        lines.append("None flagged; absence of a flag does not prove independence.")
    for item in report["exact_overlap"]:
        lines.append(f"- Exact provenance overlap: {_safe(item['left'])} / {_safe(item['right'])} — {_safe(item['reason'])}")
    for item in report["semantic_overlap_review"]:
        lines.append(
            f"- Semantic review: {_safe(item['left'])} / {_safe(item['right'])} "
            f"(bidirectional entailment {item['forward_entailment']:.2f}/{item['reverse_entailment']:.2f}); read both originals."
        )
    lines.extend(["", "## Missing or unproven", ""])
    lines.extend(f"- {_safe(gap)}" for gap in report["gaps"])
    lines.extend(["", "## Source records", "", "| ID | Kind | Voice | Channel | Date | Observation | URL |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for item in report["records"]:
        values = (item["id"], item["kind"], item["voice"], item["channel"], item["published_at"], item["observation"], item["url"])
        lines.append("| " + " | ".join(_safe(value) for value in values) + " |")
    lines.extend(["", f"Model: {report['model']}", report["warning"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit manually collected product evidence with a local NLI model")
    parser.add_argument("packet", type=Path, help="curated JSON evidence packet")
    parser.add_argument("--out", type=Path, required=True, help="Markdown report path")
    parser.add_argument("--json-out", type=Path, help="optional machine-readable report path")
    args = parser.parse_args(argv)
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
        normalized = validate_packet(packet)
        needs_model = sum(item["kind"] == "pain" and item["voice"] == "first_hand" for item in normalized["evidence"]) >= 2
        report = audit(normalized, LocalNLI() if needs_model else None)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_markdown(report), encoding="utf-8")
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"CounterSignal error: {exc}", file=sys.stderr)
        return 2
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
