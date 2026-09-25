from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"


# Embedding model required by the assignment
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# Load the local embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


# Create a persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))


# Create or load the collection
collection = chroma_client.get_or_create_collection(
    name="zepto_policy_corpus",
    metadata={"hnsw:space": "cosine"},
)


def load_documents():
    """Load all 8 policy documents from the docs folder."""
    documents = []
    ids = []
    metadatas = []

    for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(text)
        ids.append(file_path.stem)
        metadatas.append({"source": file_path.name})

    return documents, ids, metadatas


def chunk_documents(documents, ids, metadatas):
    """
    Create one chunk per document.

    The assignment allows a simple per-document chunk because
    the policy documents are short.
    """
    chunks = []
    chunk_ids = []
    chunk_metadatas = []

    for document, doc_id, metadata in zip(documents, ids, metadatas):
        chunks.append(document)
        chunk_ids.append(f"{doc_id}_chunk_01")
        chunk_metadatas.append(metadata)

    return chunks, chunk_ids, chunk_metadatas


def build_vector_database():
    """Load, chunk, embed, and store all documents in ChromaDB."""
    documents, ids, metadatas = load_documents()

    chunks, chunk_ids, chunk_metadatas = chunk_documents(
        documents,
        ids,
        metadatas,
    )

    if not chunks:
        raise ValueError("No policy documents were found in the docs folder.")

    embeddings = embedding_model.encode(
        chunks,
        normalize_embeddings=True,
    ).tolist()

    collection.upsert(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=chunk_metadatas,
    )

    return len(chunks)


def retrieve_documents(query, top_k=3):
    """Embed a query and retrieve the top-k chunks using cosine similarity."""
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True,
    )[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    retrieved = []

    result_ids = results.get("ids", [[]])[0]
    result_documents = results.get("documents", [[]])[0]
    result_metadatas = results.get("metadatas", [[]])[0]
    result_distances = results.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(
        result_ids,
        result_documents,
        result_metadatas,
        result_distances,
    ):
        retrieved.append(
            {
                "id": chunk_id,
                "document": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved


if __name__ == "__main__":
    count = build_vector_database()

    print(f"Embedded and stored {count} chunks in ChromaDB.")
    print(f"ChromaDB location: {CHROMA_DIR}")