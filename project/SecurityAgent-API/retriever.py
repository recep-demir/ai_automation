import logging
import os
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


PERSIST_DIRECTORY = "./chroma_db"

def run_retrieval(query):
    try:
        embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        logging.info(f"Loading vector database from {PERSIST_DIRECTORY}...")
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings
        )


    except Exception as e:
        logging.error(f"An error occurred during retrieval: {str(e)}")
        return []