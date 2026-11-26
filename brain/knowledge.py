from pathlib import Path
from sentence_transformers import SentenceTransformer

DOCUMENT = Path(__file__).parent / "rehber.md"

model = SentenceTransformer("google/embeddinggemma-2")


class Knowledge:
    def __init__(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.chunks = [part.strip() for part in text.split("\n\n") if part.strip()]
        self.vectors = model.encode(self.chunks, prompt_name="Document")

    def retrieve(self, question, k=2):
        question_vector = model.encode(question, prompt_name="SearchQuery")
        scores = model.similarity(question_vector, self.vectors)[0].tolist()
        ranked = sorted(zip(scores, self.chunks), reverse=True)
        return "\n".join(chunk for score, chunk in ranked[:k])
