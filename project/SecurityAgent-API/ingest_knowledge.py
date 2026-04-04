import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma
from config import Config 


logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - [Ingestion] - %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)

SOURCE_FILE = "./it_policy.txt"

def run_ingestion():
    """
    Executes the End-to-End data ingestion pipeline.
    """

    if not os.path.exists(SOURCE_FILE):
        logging.error(f"Source file '{SOURCE_FILE}' not found. Ingestion aborted.")
        return
    
    try:

        logging.info(f"Loading document: {SOURCE_FILE}")
        loader = TextLoader(SOURCE_FILE, encoding="utf-8")
        documents = loader.load()
        logging.info(f"Successfully loaded {len(documents)} document(s).")

        logging.info("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=100, 
            separators=["\n\n", "\n", " ", ""]
        )
        docs = text_splitter.split_documents(documents)
        logging.info(f"Documents split into {len(docs)} chunks.")

        logging.info(f"Initializing Embedding Model: {Config.EMBEDDING_MODEL}")
        embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)


        logging.info(f"Creating Vector Store at: {Config.VECTOR_DB_PATH}")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=Config.VECTOR_DB_PATH 
        )
        
        logging.info("🎉 SUCCESS! Knowledge Base is ready and persisted.")

    except Exception as e:
        logging.error(f"❌ CRITICAL ERROR during ingestion: {str(e)}")

if __name__ == "__main__":
    run_ingestion()