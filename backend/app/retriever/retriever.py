import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import json

def get_ensemble_retriever(k_text: int, k_img: int, k_bm25: int, weight_text: float, weight_img: float, weight_bm25: float) -> EnsembleRetriever:

    embedding_llm = OllamaEmbeddings(model="bge-m3")

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

    with open('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2/backend/process_image_20250507_120228.json', 'r', encoding='utf-8') as f:
        img_content = json.load(f)
    
    with open('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2/backend/process_text_20250507_120228.json', 'r', encoding='utf-8') as f:
        text_content = json.load(f)
    
    bm25_ls = text_content + img_content
    docs = [Document(page_content=item["page_content"], metadata=item["metadata"]) for item in bm25_ls]

    retriever_bm25 = BM25Retriever.from_documents(docs)
    retriever_bm25.k = k_bm25
    retriever_text = text_vector_store.as_retriever(search_kwargs={"k": k_text})
    retriever_image = image_vector_store.as_retriever(search_kwargs={"k": k_img})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[retriever_text, retriever_image, retriever_bm25],
        weights=[weight_text, weight_img, weight_bm25],
    )

    return ensemble_retriever

if __name__ == "__main__":
    retriever = get_ensemble_retriever(6, 5, 4, 0.4, 0.3, 0.3)
    query = "What is IAC?"
    results = retriever.invoke(query)

    print(f"Rank1: {results[0]}")
    print("="*60)
    print(f"Rank2: {results[1]}")
    print("="*60)

    text_ls = []
    img_ls = []
    for result in results:
        if result.metadata["type"] == "text":
            text_ls.append(result)
        else:
            img_ls.append(result)
    for text in text_ls:
        print(text.page_content)
        print("="*60)
    for img in img_ls:
        print(img.metadata["image_path"])
        print("="*60)