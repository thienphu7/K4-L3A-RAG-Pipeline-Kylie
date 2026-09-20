"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .contracts import validate_document

load_dotenv()


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    # TODO: Dispatch theo EMBEDDING_PROVIDER trong .env.
    #
    # Provider local gợi ý:
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer(EMBEDDING_MODEL)
    # return model.encode(texts).tolist()
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    if provider == "openai":
        from openai import OpenAI
        response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).embeddings.create(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), input=texts
        )
        return [item.embedding for item in response.data]
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL))
    return model.encode(texts, normalize_embeddings=True).tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    # TODO: Tạo hoặc mở persistent collection.
    #
    # import chromadb
    # CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    # client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # return client.get_or_create_collection(
    #     name=COLLECTION_NAME,
    #     metadata={"hnsw:space": "cosine"},
    # )
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    # TODO: Đọc mọi .md và tạo Document theo contract.
    #
    # documents = []
    # for path in STANDARDIZED_DIR.rglob("*.md"):
    #     doc_type = "legal" if "legal" in path.parts else "news"
    #     documents.append({
    #         "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
    #         "content": path.read_text(encoding="utf-8"),
    #         "metadata": {
    #             "source": path.name,
    #             "title": path.stem,
    #             "doc_type": doc_type,
    #             "url": None,
    #         },
    #     })
    # return documents
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        item = {"id": path.relative_to(STANDARDIZED_DIR).as_posix(), "content": content,
                "metadata": {"source": path.name, "title": path.stem,
                             "doc_type": "legal" if "legal" in path.parts else "news", "url": None}}
        validate_document(item)
        documents.append(item)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    # TODO: Chunk bằng RecursiveCharacterTextSplitter.
    #
    # from langchain_text_splitters import RecursiveCharacterTextSplitter
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=CHUNK_SIZE,
    #     chunk_overlap=CHUNK_OVERLAP,
    #     separators=["\n\n", "\n", ". ", " ", ""],
    # )
    # chunks = []
    # for document in documents:
    #     for index, text in enumerate(splitter.split_text(document["content"])):
    #         chunks.append({
    #             "id": f"{document['id']}::chunk-{index}",
    #             "content": text,
    #             "metadata": {**document["metadata"], "chunk_index": index},
    #         })
    # return chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
                                               separators=["\n\n", "\n", ". ", " ", ""])
    chunks = []
    for document in documents:
        for index, text in enumerate(splitter.split_text(document["content"])):
            text = text.strip()
            if text:
                chunks.append({"id": f"{document['id']}::chunk-{index}", "content": text,
                               "metadata": {**document["metadata"], "chunk_index": index}})
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    # TODO: Embed theo batch và giữ nguyên các field của chunk.
    #
    # vectors = embed_texts([chunk["content"] for chunk in chunks])
    # for chunk, vector in zip(chunks, vectors):
    #     chunk["embedding"] = vector
    # return chunks
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("embedding count does not match chunk count")
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    # TODO: Upsert ids, documents, embeddings và metadatas.
    #
    # collection = get_collection()
    # collection.upsert(
    #     ids=[chunk["id"] for chunk in chunks],
    #     documents=[chunk["content"] for chunk in chunks],
    #     embeddings=[chunk["embedding"] for chunk in chunks],
    #     metadatas=[chunk["metadata"] for chunk in chunks],
    # )
    if not chunks:
        return
    get_collection().upsert(ids=[c["id"] for c in chunks], documents=[c["content"] for c in chunks],
                            embeddings=[c["embedding"] for c in chunks], metadatas=[c["metadata"] for c in chunks])


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
