import os
import logging
from typing import List, Optional
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

PERSIST_DIRECTORY = "./chroma_db"

def validate_environment():
    """
    Checks if all required environment variables are set.
    """
    required_keys = ["GROQ_API_KEY", "EMBEDDING_MODEL"]
    for key in required_keys:
        if not os.getenv(key):
            logging.critical(f"Environment Variable Error: {key} is not set.")
            raise EnvironmentError(f"Missing configuration for {key}")

def get_ai_support(query: str) -> str:
    """
    Retrieves relevant context from ChromaDB and synthesizes an answer using Groq.
    """
    try:
        validate_environment()

        embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        
        logging.info("Connecting to ChromaDB...")
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings
        )

        logging.info(f"Retrieving context for query: {query}")

        search_results = vectorstore.similarity_search(query, k=3)
        
        if not search_results:
            return "I couldn't find any relevant company policy regarding this issue."

        retrieved_context = "\n---\n".join([doc.page_content for doc in search_results])


        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        system_message = (
            "You are a Senior IT Support Specialist. "
            "Use ONLY the following context to answer the user's question. "
            "If the answer is not in the context, say that you don't know based on company policy. "
            "Do not make up facts or use external knowledge. "
            "Keep your tone professional and technical.\n\n"
            f"### CONTEXT FROM COMPANY POLICY:\n{retrieved_context}"
        )

        logging.info("Generating response with Groq (Llama-3)...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Issue: {query}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1  
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        logging.error(f"RAG Synthesis Error: {str(e)}")
        return "System Error: I am unable to provide support at this moment."

if __name__ == "__main__":
    test_query = "What should I do if a brute force attack is detected?"
    print("\n--- AI SUPPORT RESPONSE ---")
    response = get_ai_support(test_query)
    print(response)