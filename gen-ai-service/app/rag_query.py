import os
import json
import pickle
import faiss
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.docstore.in_memory import InMemoryDocstore

from langchain_community.vectorstores import FAISS

load_dotenv()

PERSIST_DIR = "data/fastapi"
CHUNKS_FILE = f"{PERSIST_DIR}/chunks.json"
INDEX_FILE = f"{PERSIST_DIR}/index.faiss"
METADATA_FILE = f"{PERSIST_DIR}/metadata.pkl"


def load_index_and_docs():
    # Load index
    index = faiss.read_index(INDEX_FILE)

    # Load metadata
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)

    # Load chunks
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunk_data = json.load(f)

    # Convert to Document objects
    documents = []
    for item in chunk_data:
        documents.append(Document(page_content=item["chunk"], metadata={"source": item["source"]}))

    return index, documents


def run_rag_query(question):
    print("🔄 Loading index and documents...")
    index, documents = load_index_and_docs()

    # Load embeddings
    embeddings = OpenAIEmbeddings()

    # Create FAISS retriever
    docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})

    # Map FAISS index IDs to docstore keys
    index_to_docstore_id = {i: str(i) for i in range(len(documents))}

    # Create FAISS vector store manually
    db = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # Prompt Template
    prompt_template = PromptTemplate.from_template(
        """      
        You are a senior coder who values code ethics and follows strict coding guidelines. 
        You do peer reviews for merge requests and address the concerns.
        
        Address the following concerns:
        1. High level diff Analysis
        2. Security Issue Detection
        3. Code Smell Detection
        4. Improvement Suggestions
        5. future risks (if any)
        
        Following is the pull request diff:
        {question}        
        
        Use the following code snippets to address the issues.

        Code Context:
        {context}

        Provide a helpful and technically accurate answer."""
    )

    # Setup LLM QA chain
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key= os.environ['OPEN_AI_SECRET_KEY'] # Pass the key here
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template}
    )

    print("🤖 Querying LLM with context...")
    answer = qa_chain.run(question)
    print("\n✅ Answer:")
    print(answer)
    print("="*80)
    return answer


# if __name__ == "__main__":
#     # q = input("💬 Ask your codebase a question:\n> ")
#     run_rag_query(diff)
