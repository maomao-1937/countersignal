"""English NLI inference. Weights download once, then inference stays local."""

from __future__ import annotations

MODEL_ID = "cross-encoder/nli-MiniLM2-L6-H768"


class LocalNLI:
    def __init__(self) -> None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        self.model.eval()

    def entailment(self, premise: str, hypothesis: str) -> float:
        import torch

        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=512)
        with torch.inference_mode():
            logits = self.model(**inputs).logits[0]
        labels = {str(value).lower(): int(key) for key, value in self.model.config.id2label.items()}
        index = labels.get("entailment")
        if index is None:
            raise RuntimeError("NLI model does not expose an entailment label")
        return float(logits.softmax(dim=-1)[index])
