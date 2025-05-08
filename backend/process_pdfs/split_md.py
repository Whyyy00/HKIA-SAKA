from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
import os
from datetime import datetime
import re
from typing import Union, List

def split_by_header(file_path: Union[str, os.PathLike]) -> List[Document]:
    """Split a markdown file into chunks based on headers

    Args:
        file_path (Union[str, os.PathLike]): file path

    Returns:
        List[Document]: a list of langchain Document type chunks
    """

    # read the markdown
    if not file_path.endswith('.md'):
        raise ValueError(f"{file_path} is not a markdown file.")
    try:    
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()  
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} is not found.")
    
    # initialize the splitter
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header1"), ("##", "Header2")],
        strip_headers=False # contain header in the chunk
    )

    # split the markdown
    splitted_doc_list = header_splitter.split_text(content)

    # add title and added time as metadata for better reference
    for doc in splitted_doc_list:
        # extract the file name wihout '.md' as title
        doc.metadata["source_manual"] = re.sub(r"\.md$", "", os.path.basename(file_path))
        doc.metadata["added_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        doc.metadata["type"] = "text"

    return splitted_doc_list

if __name__ == "__main__":

    # ls = split_by_header("xxx.pdf")
    # ls = split_by_header("xxx.md")

    chunk_list = split_by_header("backend/data/extracted/IAC/cleaned_markdown/IAC Manual v9.md")
    for doc in chunk_list:
        print(doc)
        print("="*60)