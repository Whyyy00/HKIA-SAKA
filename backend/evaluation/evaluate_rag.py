import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
)
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaEmbeddings
from backend.app.llm.llm import get_Ollama_model
from dotenv import load_dotenv
import os

load_dotenv()
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

def evaluate_rag(file: str):
    with open(file) as f:
        data = json.load(f)

    question_ls = []
    contexts_ls = []
    answer_ls = []

    text_hit_cnt = 0
    img_hit_cnt = 0
    full_hit_cnt = 0
    coverage_recall_ls = []

    for dict in data:
        question_ls.append(dict.get('question'))
        contexts_ls.append(dict.get('contexts'))
        answer_ls.append(dict.get('answer'))

        # calculate hit recall
        top_docs = dict.get('top_docs_id')
        text_ref_ls = dict.get('text_ref_ids')
        img_ref_ls = dict.get('img_ref_ids')
        ref_ls = text_ref_ls + img_ref_ls

        # check hit or not
        text_hit = int(any(id in text_ref_ls for id in top_docs))
        img_hit = int(any(id in img_ref_ls for id in top_docs))
        full_hit = int(any(id in ref_ls for id in top_docs))

        # calculate coverage recall
        coverage_recall = len(set(top_docs) & set(ref_ls)) / len(ref_ls)

        # add to count
        text_hit_cnt += text_hit
        img_hit_cnt += img_hit
        full_hit_cnt += full_hit
        coverage_recall_ls.append(coverage_recall)

    # calculate hit recall
    text_hit_recall = text_hit_cnt / len(data)
    img_hit_recall = img_hit_cnt / len([item for item in data if item.get('img_ref_ids')])
    full_hit_recall = full_hit_cnt / len(data)

    # constuct evaluation dataset
    eval_dataset = {
        "question": question_ls,
        "answer": answer_ls,
        "contexts": contexts_ls
    }
    eval_dataset = Dataset.from_dict(eval_dataset)

    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY
    )
    embedding_llm = OllamaEmbeddings(model="bge-m3")
    eval_llm = LangchainLLMWrapper(llm)

    # evaluate
    result = evaluate(
        dataset=eval_dataset,
        metrics=[answer_relevancy, faithfulness],
        llm=eval_llm,
        embeddings=embedding_llm
    )
    df = result.to_pandas()

    df.to_csv("backend/evaluation/evaluation_result.csv")

    answer_relevancy_metrics = df['answer_relevancy'].mean()
    faithfulness_metrics = df['faithfulness'].mean()

    print(f"answer_relevancy: {answer_relevancy_metrics}")
    print(f"faithfulness: {faithfulness_metrics}")

    print(f"text_hit_recall: {text_hit_recall}")
    print(f"img_hit_recall: {img_hit_recall}")
    print(f"full_hit_recall: {full_hit_recall}")
    print(f"coverage_recall: {sum(coverage_recall_ls) / len(coverage_recall_ls)}")

if __name__ == '__main__':
    evaluate_rag(file="backend/data/evaluation/ragas_dataset_Straightforward_20250519_225324.json")

    