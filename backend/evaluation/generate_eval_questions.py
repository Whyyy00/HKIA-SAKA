import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from backend.app.llm.llm import get_Ollama_model
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from typing import Tuple, List
from datetime import datetime
import json
import os

def generate_question(page_content: str) -> str:
    llm = get_Ollama_model(task='chat')
    system_prompt = """You are an expert at generating high-quality test questions for evaluating RAG systems.
    Based on the given document content, generate a specific and clear question that can be answered using the content.

    Make sure the question:
    - Is specific and unambiguous
    - Can be answered using only the given content
    - Tests understanding rather than just fact recall
    - Is relevant to airport operations and management
    - Is natural to be asked by a real staff in daily life (in casual tone)

    Return the quesiton only without other explanations.
    """

    messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=page_content)
        ]

    response = llm.invoke(messages)

    return response.content

def get_all_docs() -> Tuple[List[Document], List[Document]]:
    # initialize llm and embedding
    embedding_llm = OllamaEmbeddings(model="bge-m3")
    
    # get db
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
    
    # initialize the retriever
    retriever_text = text_vector_store.as_retriever(search_kwargs={"k": 67})
    retriever_image = image_vector_store.as_retriever(search_kwargs={"k": 59})

    # get all docs in the vbector sotre
    text_docs = retriever_text.invoke(" ")
    img_docs = retriever_image.invoke(" ")

    return text_docs, img_docs

def generate_eval_questions(dir: str = "backend/data/evaluation"):
    # get docs
    text_docs, img_docs = get_all_docs()

    # initialize the question dict list
    question_dict_ls = []

    # generate question for all docs
    for i, doc in enumerate(text_docs):
        print(f"正在处理第{i+1}个片段 / 共{len(text_docs)}个")

        # initialze the question dict
        question_dict = {}
        
        # get content and infos of  each doc
        text_ref_id = doc.id
        content = doc.page_content
        header1 = doc.metadata.get('Header1')
        header2 = doc.metadata.get('Header2')

        # format the query
        content_query = f"# {header1}\n{content}"

        # generate question for the doc
        question = generate_question(content_query)

        # construct the quesiton dict
        question_dict['question'] = question
        question_dict['text_ref_ids'] = [text_ref_id]
        question_dict['img_ref_ids'] = [img_doc.id for img_doc in img_docs if img_doc.metadata.get('Header2') == header2]

        # add to question dict list
        question_dict_ls.append(question_dict)

    # save json file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(dir, f"eval_questions_{timestamp}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(question_dict_ls, f, ensure_ascii=False, indent=4)

    return None

if __name__ == '__main__':

    # test question generation
    # page_content = """
    # ## 9.2 Use of Personal Telecommunication Devices  
    # 9.2.1 Use of personal electronic telecommunication devices is very common nowadays. Staff must concentrate at their job duties at IAC and minimize  
    # the use of personal electronic telecommunication devices in whatever ways including telephone calls or using any applications.  
    # 9.2.2 Ring tone of all personal electronic telecommunication devices and TMRs must be turned down, or changed to silent mode if possible, so that it will not cause any disturbance to other IAC staff of performing their job duties.  
    # 9.2.3 If the information to be accessed using desktop, laptop or mobile devices is sensitive or treated as confidential to companies, staff should follow the corresponding policies of their companies or consult their supervisors or responsible departments in advance.
    # """
    # question = generate_question(page_content)
    # print(question)

    # page_content = """
    # # Part 3 Incident & Emergency Handling and Reporting
    # ## 3.23 Dangerous Goods and Chemical Spills (EPM Part 15)
    # ## 3.23.1 There is a range of dangerous goods and other chemicals stored, handled, and used at the HKIA. The checklist below summarized the action items:
    # """
    # question = generate_question(page_content)
    # print(question)

    # # test get docs from vector store
    # text_docs, img_docs = get_all_docs()
    # print(text_docs[0])
    # print("="*60)
    # print(img_docs[0])

    generate_eval_questions()