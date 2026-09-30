"""Week 1, Block 5: build a searchable index over plan documents.

The agent uses this to answer benefits questions WITH citations.

Learn first:
    - What an embedding is and why similar text lands close together
    - Chunking: why you split documents, and how chunk size changes results
    - Why every answer should cite the chunk it came from

Run:
    python -m src.retrieval.index            # build the index
    python -m src.retrieval.index "Is an MRI covered?"   # test a query
"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb

DOCS_DIR = Path("data/plan_docs")
DB_DIR = Path("data/chroma")
COLLECTION = "plan_docs"


def load_docs() -> list[tuple[str, str]]:
    """Return (filename, text) for every markdown plan document."""
    return [(p.name, p.read_text()) for p in sorted(DOCS_DIR.glob("*.md"))]


def chunk(text: str, source: str) -> list[dict]:
    """Split one document into chunks.

    TODO (you): start simple. Split on markdown headings ("## "), so each
    benefit section is one chunk. Return a list of
        {"id": "<source>#<n>", "text": "...", "source": source, "section": "<heading>"}
    Later, experiment with fixed-size chunks and compare retrieval quality.
    """
    raise NotImplementedError("Week 1, Block 5: implement chunk")


def build() -> None:
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_or_create_collection(COLLECTION)  # default local embedding model
    chunks = [c for name, text in load_docs() for c in chunk(text, name)]
    col.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "section": c["section"]} for c in chunks],
    )
    print(f"indexed {len(chunks)} chunks")


def search(query: str, k: int = 3) -> list[dict]:
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_collection(COLLECTION)
    res = col.query(query_texts=[query], n_results=k)
    return [
        {"text": doc, **meta, "distance": dist}
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for hit in search(" ".join(sys.argv[1:])):
            print(f"[{hit['source']} > {hit['section']}] ({hit['distance']:.3f})\n{hit['text'][:200]}\n")
    else:
        build()
