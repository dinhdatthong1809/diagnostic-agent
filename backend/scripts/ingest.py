"""Nạp tài liệu y khoa trong app/rag/knowledge_base vào Chroma vector store.

Chạy: python -m scripts.ingest  (từ thư mục backend/, sau khi cài requirements.txt)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app.config import CHROMA_DIR, KNOWLEDGE_BASE_DIR
from app.rag.chain import get_embeddings


def main():
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    if not docs:
        print(f"Không tìm thấy tài liệu .md nào trong {KNOWLEDGE_BASE_DIR}")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    os.makedirs(CHROMA_DIR, exist_ok=True)
    Chroma.from_documents(chunks, get_embeddings(), persist_directory=CHROMA_DIR)

    print(f"Đã nạp {len(docs)} tài liệu -> {len(chunks)} đoạn vào vector store tại {CHROMA_DIR}")


if __name__ == "__main__":
    main()
