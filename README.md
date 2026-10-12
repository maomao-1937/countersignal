# CounterSignal

CounterSignal helps an independent maker inspect **manually collected** product-idea evidence before coding. It highlights repeated authors/threads, uses a real local natural-language-inference (NLI) model to flag potentially overlapping pain statements, and lists evidence gaps. It does **not** say “build” or invent market sizes.

## Who and when

Use it when you have read a handful of public posts, reviews or support requests about one product idea and want to avoid counting the same complaint as multiple independent users. The workflow is: read the originals → curate a small JSON packet → run a local audit → inspect flagged pairs → interview or observe users. This is a review aid, not demand validation by itself.

## Install and run

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/). The first run downloads the [Apache-2.0 English NLI model](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768); subsequent inference is local. No model API key is required. The app does not fetch evidence URLs, upload your packet, or post to any community. Do not include private customer data in a report you plan to share.

```bash
uv sync --python 3.11
uv run countersignal examples/synthetic.json --out report.local.md --json-out report.local.json
cat report.local.md
uv run python -m unittest discover -s tests -v
```

The example is **synthetic**; the URLs on `example.org` are placeholders, not users or demand evidence. The model really evaluates the provided English claim pairs and currently flags `pain-a` / `pain-b` for review. Scores may vary with model/runtime; no sample output is pre-recorded or substituted for inference. The Markdown report has coverage, possible duplicate records, missing evidence, and links back to source records; the JSON report is machine-readable.

## Packet format

```json
{
  "schema_version": 1,
  "idea": {
    "name": "Example idea",
    "target_user": "Independent makers",
    "problem": "A specific repeated job may be underserved"
  },
  "evidence": [
    {
      "id": "p1",
      "kind": "pain",
      "voice": "first_hand",
      "channel": "reddit",
      "author": "public-handle-or-local-alias",
      "published_at": "2026-06-01",
      "url": "https://example.org/post/1",
      "thread_url": "https://example.org/post/1",
      "claim": "I repeatedly miss client invoice reminders.",
      "observation": "The author says they use a spreadsheet to remind clients."
    }
  ]
}
```

`kind` is `pain`, `workaround`, `counter`, `competitor`, or `attention`; `voice` is `first_hand`, `reported`, or `product_claim`. `claim` should be a short English paraphrase of **what this record supports**, not an AI-invented conclusion. `observation` records the actual behavior or caveat; preserve the source URL for human review. Use the same `thread_url` for comments under one discussion. Record a competitor's product page as `kind=competitor` but do not treat its marketing copy as user demand. The current limit is 40 records and 20 first-hand pain records per packet.

For private interviews, keep the packet local and use a permitted internal URL; do not publish interview text or identifiers. CounterSignal intentionally has no scraping, login, telemetry, web search or auto-posting.

## How to interpret results

- Exact provenance overlap is based on a matching channel/author identity or discussion URL. Handles are user-supplied and aliases across platforms cannot be identified automatically.
- Semantic overlap is a **review suggestion** when the English NLI model gives high entailment in both directions. Similar wording may describe different jobs; different wording may describe the same job. Neither is an independent-user count or calibrated probability of truth.
- Coverage checks are mechanical: first-hand identities, channels, time span, plus whether counter-evidence, workarounds and competitors were recorded. A missing flag means only that no record of that type was supplied.
- Public complaints cannot demonstrate willingness to switch, pay, retain or recommend. You still need interviews, observed behavior, and a product experiment.

The present wedge differs from [IdeaOne](https://ideaone.dev/) and [Preuve](https://preuve.ai/idea-validation/): those services discover and score ideas from live sources, while this tool audits evidence you already inspected, entirely locally after model download, and deliberately refuses a numeric idea score. [Reddit Demand Validator](https://github.com/SevenAILab/reddit-demand-validator) already provides a strong Reddit-only research memo and falsification workflow; CounterSignal is a small cross-channel, machine-executable overlap check, not a replacement for its research process. [RigorGraph](https://github.com/f0909172434/rigorgraph) is a broader evidence graph and audit framework. These differences are testable product hypotheses, **not** proof that users prefer this tool.

## Why this was chosen, and limits

In an [August 2025 HN discussion](https://news.ycombinator.com/item?id=44881440), independent users tested an AI idea validator with absurd inputs and questioned repeated scores and unsupported market estimates. In [2026 Reddit discussions](https://www.reddit.com/r/SaaS/comments/1v8xx4e/how_do_you_use_ai_to_validate_startup_ideas/), users described reading original posts and clustering recurring complaints rather than trusting a single hot thread; another [hands-on validator comparison](https://www.reddit.com/r/Startup_Ideas/comments/1vhkcut/i_tested_ai_idea_validators_so_you_dont_have_to/) stressed missing willingness-to-pay and unit-economics evidence. Those are recurring problem signals, not measured adoption for CounterSignal. See the [dated selection audit](docs/selection.md) for alternatives and counter-evidence.

The model is English-trained and may miss negation, numerical details, sarcasm, domain jargon or non-English paraphrases. Long claims are truncated at 512 model tokens. The tool never verifies that a URL exists, an author is genuine, a post is representative, or a competitor has been comprehensively found. It never collapses AI-suggested pairs into a “unique demand” number. Limits and model scores should remain visible when sharing the report.

MVP acceptance is a clean install, genuine local-model run on the synthetic packet, passing automated tests, reviewable original-record links, and no uploaded evidence or invented market verdict. Real-user usefulness, time saved, and attention potential are **not yet validated**.

Application code: MIT license. Model weights are downloaded separately under their own Apache-2.0 license; no reference-project code or prompts are copied.
