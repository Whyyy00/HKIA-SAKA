import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from backend.process_pdfs.split_md import split_by_header
from backend.process_pdfs.get_images import get_context_with_image_path
from backend.app.llm.llm import summarize_images_with_context
from typing import List, Tuple
from langchain_core.documents import Document
import re
import os

def remove_img_link(content: str) -> str:
    """After extract image content, remove the image links in markdown content to get better embeddings.

    Args:
        content (str): markdown content

    Returns:
        str: clean markdown content without image links
    """
    result = re.sub(r"!\[\]\((.*)\)", "", content)
    return result

import json
from datetime import datetime

def save_documents_to_json(documents, file_path):
    """Save docs into json
    
    Args:
        documents (List[Document]): 
        file_path (str): 
    """

    serializable_docs = []
    for doc in documents:
        doc_dict = {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        serializable_docs.append(doc_dict)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_docs, f, ensure_ascii=False, indent=2)
    
    print(f"已保存{len(serializable_docs)}个文档到 {file_path}")

def get_documents() -> Tuple[List[Document], List[Document]]:
    # split the IAC manual by header
    splitted_iac = split_by_header("backend/data/extracted/IAC/cleaned_markdown/IAC Manual v9.md")

    # splitted_iac = splitted_iac[:12]

    print(f"总共有{len(splitted_iac)}个chunks.")
    print("="*60)

    img_ls = []
    # Go through each doc in spllited_iac and extract image infos for it
    for i, doc in enumerate(splitted_iac):
        print(f"正在处理第{i+1}个chunk")
        content = doc.page_content
        image_with_context = get_context_with_image_path(content)
        print(f"该chunk有{len(image_with_context)}张图片")
        for i, img_dic in enumerate(image_with_context):
            print(f"正在处理第{i+1}张图片")
            # add manual infos into context
            context = f"This is a image from the manual: {doc.metadata["source_manual"]} - {doc.metadata["Header1"]}.\
                The context is: {img_dic["context"]}"
            # get image path based on root dir
            img_folder_path = "backend/data/extracted/IAC/images"
            img_path = os.path.join(img_folder_path, os.path.basename(img_dic["image_path"]))
            # get summary of image
            img_summary = summarize_images_with_context(context=img_dic["context"], image_path=img_path)
            # construct Document Object
            img_ls.append(Document(page_content=img_summary, 
                                   metadata={"type": "image",
                                            "source_manual": doc.metadata["source_manual"], 
                                            "Header1": doc.metadata["Header1"],
                                            "Header2": doc.metadata["Header2"],
                                            "Section": img_dic["section_number"],
                                            "image_path": img_path,
                                            "added_time": doc.metadata["added_time"]}
                                    )
                            )
        doc.page_content = remove_img_link(doc.page_content)
        print("="*60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_documents_to_json(splitted_iac, f"backend/process_text_{timestamp}.json")
    save_documents_to_json(img_ls, f"backend/process_image_{timestamp}.json")

    return splitted_iac, img_ls

if __name__ == "__main__":
    text_ls, img_ls = get_documents()
    for img in img_ls:
        print("="*60)
        print(img)