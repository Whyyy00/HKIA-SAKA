import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from backend.process_pdfs.process_pdfs import get_documents

def embed_docs() -> None:
    embedding_llm = OllamaEmbeddings(model="bge-m3")

    text_docs, image_docs = get_documents()

    text_vector_store = Chroma(
        collection_name="text_manuals_collection", 
        embedding_function=embedding_llm,
        persist_directory="backend/data/chroma_langchain_db"
    )

    image_vector_store = Chroma(
        collection_name="image_manuals_collection",
        embedding_function=embedding_llm,
        persist_directory="backend/data/chroma_langchain_db"
    )

    text_vector_store.add_documents(text_docs)
    image_vector_store.add_documents(image_docs)

if __name__ == "__main__":
    embed_docs()