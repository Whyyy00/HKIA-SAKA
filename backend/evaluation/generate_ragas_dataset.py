import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
import json
from backend.app.llm.rag_query import rag_query_stream
from typing import Literal
from datetime import datetime
import os

def generate_dataset(mode: Literal['Straightforward', 'Comprehensive'], file: str, output_dir: str = "backend/data/evaluation"):
    with open(file) as f:
        data = json.load(f)
    
    ragas_dataset = []
    for i, question_dict in enumerate(data):
        print(f"正在处理第{i+1}个片段 / 共{len(data)}个")
        # initialize the item
        item = {}
        
        # get the question
        question = question_dict.get('question')
        # get rag response
        stream_iter, top_docs = rag_query_stream(question, mode=mode)
        answer = ""
        for chunk in stream_iter:
            answer += chunk
        item['question'] = question
        item['answer'] = answer
        item['contexts'] = [doc.page_content for doc in top_docs]
        item['top_docs_id'] = [doc.id for doc in top_docs]
        item['text_ref_ids'] = question_dict.get('text_ref_ids')
        item['img_ref_ids'] = question_dict.get('img_ref_ids')

        ragas_dataset.append(item)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"ragas_dataset_{mode}_{timestamp}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(ragas_dataset, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    generate_dataset(mode='Straightforward', file='backend/data/evaluation/eval_questions_20250519_204446.json')