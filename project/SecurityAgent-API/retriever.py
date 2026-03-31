import os
import logging
from typing import Any, List, Dict
from groq import AsyncGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from config import Config


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Retriever] - %(message)s'
)

class AI_Retriever:
    """
    Handles AI logic, retrieval-augmented generation (RAG), 
    and interaction with the Groq LLM.
    """

    def __init__(self):
        self.persist_directory = Config.VECTOR_DB_PATH
        self.model_name = Config.MODEL_NAME
        
        logging.info("Initializing Embedding Model and Vectorstore...")
        
        self.embeddings_model = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        
        self.vectorstore_engine = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings_model
        )
        
        self.async_groq_client = AsyncGroq(api_key=Config.GROQ_API_KEY)

    async def get_ai_support(self, query: str) -> Dict[str, Any]:
        
        try:

            logging.info(f"Querying VectorDB for: {query[:40]}...")

            search_results = self.vectorstore_engine.similarity_search(query, k=3)
            
            if not search_results:
                return {
                    "answer": "I couldn't find any relevant company policy regarding this issue.",
                    "sources": []
                }

            retrieved_context = ""
            sources = set() # Use a set to avoid duplicate source names

            for doc in search_results:
                retrieved_context += f"{doc.page_content}\n---\n"
                source_file = doc.metadata.get("source", "Unknown Source")
                sources.add(os.path.basename(source_file))

            system_message = (
                "You are a Senior IT Support Specialist. "
                "Use ONLY the following context to answer the user's question. "
                "If the answer is not in the context, say that you don't know based on company policy. "
                "Do not make up facts or use external knowledge. "
                "Keep your tone professional and technical.\n\n"
                f"### CONTEXT FROM COMPANY POLICY:\n{retrieved_context}"
            )

            logging.info(f"Generating response with {self.model_name}...")
            chat_completion = await self.async_groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Issue: {query}"}
                ],
                model=MODEL_NAME,
                temperature=0.1  
            )

            return {
                "answer": chat_completion.choices[0].message.content,
                "sources": list(sources)
            }

        except Exception as e:
            logging.error(f"RAG Synthesis Error: {str(e)}")
            raise e

if __name__ == "__main__":

    import asyncio
    
    async def main_test():
        test_query = "What should I do if a brute force attack is detected?"
        print("\n--- AI SUPPORT RESPONSE (TEST) ---")
        try:
            result = await get_ai_support(test_query)
            print(f"RESPONSE: {result['answer']}")
            print("-" * 30)
            print(f"SOURCES USED: {result['sources']}")
        except Exception as e:
            print(f"Test Failed: {e}")

    asyncio.run(main_test())