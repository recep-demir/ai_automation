import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

SOURCE_FILE = "it_policy.txt"
PERSIST_DIRECTORY = "./chroma_db"

def run_ingestion():

    if not os.path.exists(SOURCE_FILE):
        print(f"Source file '{SOURCE_FILE}' not found. Please ensure it exists.")
        return
    
    loader = TextLoader(SOURCE_FILE, encoding="utf-8")
    documents = loader.load()
    print(f"Successfully loaded {len(documents)} document(s).")

    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50) // 
    docs = text_splitter.split_documents(documents)
    print(f"Documents split into {len(docs)} chunks.")


    print("Initializing Embedding Model (this may take a moment)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Vector Database and saving to disk...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    print(f"Success! Knowledge base created at {PERSIST_DIRECTORY}")


    if __name__ == "__main__":
        run_ingestion()

