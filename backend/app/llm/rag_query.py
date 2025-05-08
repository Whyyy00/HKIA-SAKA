import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from backend.app.retriever.retriever import get_ensemble_retriever
from backend.app.llm.llm import get_Ollama_model
from langchain_core.documents import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from typing import List, Tuple

def rag_query(query: str) -> Tuple[str, List[str]]:

    # initialize llm and retriever
    llm = get_Ollama_model(task='chat')
    retriever = get_ensemble_retriever(3, 3, 0.6, 0.5)

    # retrieve top 2 docs
    retrieved_docs = retriever.invoke(query)
    top_docs = retrieved_docs[:4]

    def format_docs(docs: List[Document]) -> str:
        formatted_context = "\n\n".join([f"The {i+1}th snippet: \n{doc.metadata['source_manual'].strip()} - {doc.metadata['Header1'].strip()} \
                                        - {doc.metadata['Header2'].strip()}\n{doc.page_content}" \
                                        for i, doc in enumerate(docs)])
        return formatted_context
    
    formatted_context = format_docs(top_docs)

    # print(formatted_context)

    # contruct rag chain
    template = '''You are SAKA, a professional AI assistant specialized in providing precise, 
    step-by-step guidance based on airport manuals. Your primary users are frontline airport staff 
    who need clear and concise instructions to perform their tasks efficiently.
    
    Relevant manual snippets:
    {context}

    User's qustion: {question}

    Answer:"""
    '''

    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": lambda _: formatted_context, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Answer
    stream_iter = rag_chain.stream(query)

    # Image path list
    img_path_ls  = [doc.metadata['image_path'] for doc in top_docs if doc.metadata['type'] == 'image']

    return stream_iter, img_path_ls

if __name__ == "__main__":
    question = "What should be done if there is fire in Fire in Passenger Terminal Building?"
    answer, img_ls = rag_query(question)
    print(f"Question: {question}")
    buffer = ""

    for chunk in answer:
        buffer += chunk
        if buffer.endswith(" "): 
            print(buffer, end="", flush=True)
            buffer = ""

    if buffer:
        print(buffer, end="", flush=True)

    print("\n", img_ls)