import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from backend.app.retriever.retriever import get_ensemble_retriever
from backend.app.llm.llm import get_Ollama_model
from langchain_core.documents import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from typing import List, Tuple, Literal

def rag_query(query: str, mode: Literal['Straightforward', 'Comprehensive']) -> Tuple[str, List[str]]:

    # initialize llm and retriever
    llm = get_Ollama_model(task='chat')
    retriever = get_ensemble_retriever(6, 5, 4, 0.4, 0.3, 0.3)

    # rewrite the query
    def rewrite_query(query: str) -> str:
        rewrite_template = """You are an expert assistant in airport operations. Your task is to understand the user's true intent and rewrite their query to improve retrieval quality.
        Original query: {query}
        Please analyze the user's potential underlying intent and rewrite the query to make it more specific and detailed, so that it better matches the content in the airport operations manual.
        Return the rewritten query without other explanation.
        Rewritten query:"""

        rewrite_prompt = ChatPromptTemplate.from_template(rewrite_template)

        rewrite_chain = (
            {"query": lambda x: x}
            | rewrite_prompt
            | llm
            | StrOutputParser()
        )

        rewritten_query = rewrite_chain.invoke(query)

        return rewritten_query

    rewritten_query = rewrite_query(query)
    
    # retrieve top 2 docs
    retrieved_docs = retriever.invoke(rewritten_query)
    top_docs = retrieved_docs[:4]

    def format_docs(docs: List[Document]) -> str:
        formatted_context = "\n\n".join([f"\n{doc.metadata['source_manual'].strip()} - {doc.metadata['Header1'].strip()} \
                                        - {doc.metadata['Header2'].strip()}\n{doc.page_content}" \
                                        for i, doc in enumerate(docs)])
        return formatted_context
    
    formatted_context = format_docs(top_docs)

    # print(formatted_context)

    # contruct rag chain
    if mode == 'Straightforward':
        template = '''You are SAKA, a professional AI assistant specialized in providing precise, 
        step-by-step guidance based on airport manuals. Your primary users are frontline airport staff 
        who need clear and concise instructions to perform their tasks efficiently. So find most relevant
        contents in provided manual infos to answer the question and in ordered list style.
        Just provide your answer directly without "Here is.... / Based on the provided contents...".
        
        Relevant manual contents:
        {context}

        User's qustion: {question}

        Answer:"""
        '''
    else:
        template = '''You are SAKA, an AI assistant providing in-depth analysis and strategic recommendations based on airport manuals.
        Your primary users are airport management personnel who require well-reasoned insights to make informed decisions.
        **Response Style:**  
        - Provide a structured response, including analysis, potential challenges, and recommendations.  
        - Use professional terminology where appropriate.  
        - Support responses with relevant references from the manuals.  
        - Where applicable, highlight best practices and industry standards. 
        - Do not start with "based on th provided manuals", just provide your answer.

        Relevant manual contents:
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
    stream_iter = rag_chain.stream(rewritten_query)

    # # Image path list
    # img_path_ls  = [doc.metadata['image_path'] for doc in top_docs if doc.metadata['type'] == 'image']

    print(f"Query: {query}")
    print("="*60)
    print(f"Rewritten query: {rewritten_query}")
    print("="*60)
    print(f"Top docs: {top_docs}")
    print("="*60)
    print(f"Context: {formatted_context}")
    print("="*60)
    
    return stream_iter, top_docs

if __name__ == "__main__":
    question = "How to handle bomb threat?"
    answer, img_ls = rag_query(question, 'Straightforward')
    
    buffer = ""

    for chunk in answer:
        buffer += chunk
        if buffer.endswith(" "): 
            print(buffer, end="", flush=True)
            buffer = ""

    if buffer:
        print(buffer, end="", flush=True)

    print("\n", img_ls)