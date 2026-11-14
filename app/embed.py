import os
from functools import lru_cache
from typing import Iterable


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str | None = None):
    name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(name)
    except Exception as error:
        raise RuntimeError(
            f"Unable to load embedding model '{name}'. "
            "The model may need to download on first use."
        ) from error


def embed_texts(texts: Iterable[str], model_name: str | None = None) -> list[list[float]]:
    values = list(texts)
    if not values or any(not isinstance(text, str) or not text.strip() for text in values):
        raise ValueError("Cannot embed an empty text input.")
    model = get_embedding_model(model_name)
    vectors = model.encode(values, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(query: str, model_name: str | None = None) -> list[float]:
    return embed_texts([query], model_name=model_name)[0]
