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


        logging.info(f"Searching for query: {query}")
        results = vectorstore.similarity_search(query, k=2)

        if not results:
            logging.warning("No relevant documents found.")
            return
        
        logging.info("--- Search Results ---")
        for i, doc in enumerate(results):
            logging.info(f"Result {i+1}:")
            logging.info(f"Content: {doc.page_content}")
            logging.info("-" * 20)
        


    except Exception as e:
        logging.error(f"An error occurred during retrieval: {str(e)}")
        return []
    

if __name__ == "__main__":
    user_query = input("Please enter your technical issue or question: ")
    if user_query:
        run_retrieval(user_query)