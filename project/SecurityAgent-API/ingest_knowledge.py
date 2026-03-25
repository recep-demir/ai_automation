import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)

def validate_config():
    required_vars = ["EMBEDDING_MODEL"]
    for var in required_vars:
        if not os.getenv(var):
            logging.critical(f"Environment variable '{var}' is missing! System exiting.")
            raise EnvironmentError(f"Missing required configuration: {var}")


validate_config()

SOURCE_FILE = "./it_policy.txt"
PERSIST_DIRECTORY = "./chroma_db"

def run_ingestion():

    if not os.path.exists(SOURCE_FILE):
        logging.error(f"Source file '{SOURCE_FILE}' not found. Please ensure it exists.")
        return
    
    try:
        logging.info("Loading document...")
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


        logging.info("Initializing HuggingFace Embedding Model...")
        embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))

        logging.info("Creating Vector Database in progress...")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY
        )
        logging.info(f"Success! Vector database saved at {PERSIST_DIRECTORY}")


    except Exception as e:
        logging.error(f"An error occurred during ingestion: {str(e)}")



if __name__ == "__main__":
    run_ingestion()

