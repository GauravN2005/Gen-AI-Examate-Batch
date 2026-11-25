"""Lightweight ONNX embedding function without PyTorch."""

from collections.abc import Iterable
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str | None = None):
    try:
        import chromadb.utils.embedding_functions as ef
        return ef.DefaultEmbeddingFunction()
    except Exception as error:
        raise RuntimeError("Unable to load ONNX embedding model.") from error


def embed_texts(texts: Iterable[str], model_name: str | None = None) -> list[list[float]]:
    values = list(texts)
    if not values or any(not isinstance(text, str) or not text.strip() for text in values):
        raise ValueError("Cannot embed an empty text input.")
    model = get_embedding_model(model_name)
    vectors = model(values)
    return [
        v.tolist() if hasattr(v, "tolist") else [float(x) for x in v]
        for v in vectors
    ]


def embed_query(query: str, model_name: str | None = None) -> list[float]:
    return embed_texts([query], model_name=model_name)[0]
