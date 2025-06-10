# ingestor.py

import os
import json
import pickle
import numpy as np
import faiss
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


SUPPORTED_EXTENSIONS = ('.py',)

PERSIST_DIR = "data/fastapi"
os.makedirs(PERSIST_DIR, exist_ok=True)

CHUNKS_FILE = os.path.join(PERSIST_DIR, "chunks.json")
INDEX_FILE = os.path.join(PERSIST_DIR, "index.faiss")
METADATA_FILE = os.path.join(PERSIST_DIR, "metadata.pkl")


def read_code_files(base_path: str):
    code_texts = []
    file_paths = []
    for root, _, files in os.walk(base_path):
        for file in files:
            print(file)
            if file.endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_texts.append(f.read())
                        file_paths.append(file_path)
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
    return code_texts, file_paths



def chunk_code(code_texts):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_chunks = []
    chunk_map = []

    for i, code in enumerate(code_texts):
        chunks = splitter.split_text(code)
        all_chunks.extend(chunks)
        chunk_map.extend([i] * len(chunks))

    return all_chunks, chunk_map


def build_embedding_index(chunks):
    embeddings = OpenAIEmbeddings()
    vectors = embeddings.embed_documents(chunks)

    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype('float32'))

    return index, vectors


def persist_chunks(chunks, chunk_map, file_paths):
    data = []
    for i, chunk in enumerate(chunks):
        source_file = file_paths[chunk_map[i]]
        data.append({"chunk": chunk, "source": source_file})
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Chunks saved to {CHUNKS_FILE}")


def persist_index(index, chunk_map, file_paths):
    faiss.write_index(index, INDEX_FILE)
    metadata = {
        "chunk_map": chunk_map,
        "file_paths": file_paths,
    }
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    print(f"💾 FAISS index saved to {INDEX_FILE}")
    print(f"💾 Metadata saved to {METADATA_FILE}")


if __name__ == "__main__":
    base_dir = r"C:\Users\NavyaYR\Downloads\fastapi-master"  # Change to your repo path

    print("🔍 Reading source files...")
    code_texts, file_paths = read_code_files(base_dir)

    print(f"📄 Found {len(code_texts)} files.")

    print("✂️ Splitting code into chunks...")
    chunks, chunk_map = chunk_code(code_texts)

    print(f"📦 Created {len(chunks)} chunks.")

    print("🔐 Embedding and indexing chunks...")
    index, vectors = build_embedding_index(chunks)

    print("✅ Index built with FAISS.")

    print("📝 Persisting chunks and index...")
    persist_chunks(chunks, chunk_map, file_paths)
    persist_index(index, chunk_map, file_paths)
