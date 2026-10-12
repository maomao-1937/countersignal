import copy
import json
from pathlib import Path
import unittest

from countersignal.cli import render_markdown
from countersignal.core import audit, validate_packet


EXAMPLE = json.loads((Path(__file__).resolve().parents[1] / "examples" / "synthetic.json").read_text())


class FakeNLI:
    def entailment(self, premise, hypothesis):
        if "tax rates" in premise or "tax rates" in hypothesis:
            return 0.02
        return 0.91


class CounterSignalTests(unittest.TestCase):
    def test_synthetic_packet_keeps_distinct_sources_and_model_signal_separate(self):
        report = audit(EXAMPLE, FakeNLI())
        self.assertEqual(report["counts"]["first_hand_pain_records"], 3)
        self.assertEqual(report["counts"]["distinct_first_hand_identities"], 3)
        self.assertEqual(report["counts"]["distinct_first_hand_threads"], 3)
        self.assertEqual(report["counts"]["first_hand_span_days"], 61)
        self.assertEqual([(x["left"], x["right"]) for x in report["semantic_overlap_review"]], [("pain-a", "pain-b")])
        self.assertEqual(report["exact_overlap"], [])
        self.assertEqual(len(report["gaps"]), 1)

    def test_same_author_and_thread_are_flagged_even_when_claims_differ(self):
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"][1]["channel"] = "community-a"
        packet["evidence"][1]["author"] = "sample-user-a"
        packet["evidence"][1]["thread_url"] = packet["evidence"][0]["thread_url"] + "?ref=reply"
        report = audit(packet, FakeNLI())
        self.assertEqual(report["counts"]["distinct_first_hand_identities"], 2)
        self.assertEqual(report["counts"]["distinct_first_hand_threads"], 2)
        self.assertEqual(report["exact_overlap"][0]["reason"], "same channel and author")

    def test_missing_sources_are_reported_without_verdict(self):
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"] = [packet["evidence"][0]]
        report = audit(packet)
        self.assertGreaterEqual(len(report["gaps"]), 5)
        self.assertNotIn("score", report)
        self.assertNotIn("verdict", report)

    def test_bad_inputs_fail_closed(self):
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"][1]["id"] = "pain-a"
        with self.assertRaisesRegex(ValueError, "duplicate evidence id"):
            validate_packet(packet)
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"][0]["url"] = "file:///private/secret"
        with self.assertRaisesRegex(ValueError, "http"):
            validate_packet(packet)
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"][0]["published_at"] = "2099-01-01"
        with self.assertRaisesRegex(ValueError, "future"):
            validate_packet(packet)

    def test_two_pains_require_real_or_injected_model(self):
        with self.assertRaisesRegex(ValueError, "real NLI model"):
            audit(EXAMPLE)

    def test_markdown_is_reviewable_and_escapes_tables(self):
        packet = copy.deepcopy(EXAMPLE)
        packet["evidence"][0]["observation"] = "manual | review"
        markdown = render_markdown(audit(packet, FakeNLI()))
        self.assertIn("manual \\| review", markdown)
        self.assertIn("https://example.org/community-a/1", markdown)
        self.assertIn("This is an evidence audit", markdown)


if __name__ == "__main__":
    unittest.main()
