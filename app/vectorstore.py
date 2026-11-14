import argparse
from pathlib import Path
from typing import Any

from app.chunking import load_chunks
from app.embed import embed_query, embed_texts


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "fundfacts_chunks"


def get_collection():
    try:
        import chromadb
        return chromadb.PersistentClient(path=str(CHROMA_DIR)).get_or_create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as error:
        raise RuntimeError("Unable to open the persistent Chroma collection.") from error


def _client():
    import chromadb

    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _metadata(chunk: dict[str, Any]) -> dict[str, Any]:
    values = {
        "source_url": chunk["source_url"],
        "title": chunk["title"],
    }
    if chunk.get("page") is not None:
        values["page"] = chunk["page"]
    if chunk.get("record_id") is not None:
        values["record_id"] = str(chunk["record_id"])
    return values


def index_chunks(chunks: list[dict[str, Any]] | None = None, rebuild: bool = False) -> int:
    collection = get_collection()
    if rebuild:
        _client().delete_collection(COLLECTION_NAME)
        collection = get_collection()
    values = chunks if chunks is not None else load_chunks()
    if not values:
        return collection.count()
    embeddings = embed_texts([chunk["text"] for chunk in values])
    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in values],
        documents=[chunk["text"] for chunk in values],
        metadatas=[_metadata(chunk) for chunk in values],
        embeddings=embeddings,
    )
    return collection.count()


def query_chunks(query: str, limit: int = 5) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("Search query cannot be blank.")
    if limit <= 0:
        raise ValueError("limit must be positive.")
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    ids = result.get("ids", [[]])[0]
    return [
        {
            "chunk_id": ids[index],
            "text": documents[index],
            **metadatas[index],
            "page": metadatas[index].get("page"),
            "distance": float(distances[index]),
        }
        for index in range(len(documents))
    ]


def count_chunks() -> int:
    return get_collection().count()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    chunks = load_chunks()
    count = index_chunks(chunks, rebuild=args.rebuild)
    print(f"Source records: {len({chunk['source_url'] for chunk in chunks})}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Indexed chunks: {count}")
    print(f"Persistent database: {CHROMA_DIR}")


if __name__ == "__main__":
    main()
