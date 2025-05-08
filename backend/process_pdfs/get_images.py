from typing import List, Dict
import re

def get_context_with_image_path(content: str) -> List[Dict]:
    """Extract context and image path from the content(chunked markdown).
    For IAC docs, it extract the content before a image starting from the header `x.x.x` as the context.
    
    Args:
        content (str): the markdown content

    Returns:
        List[Dict]: return a list of dictionaries, containing section_number, context, image_path
    """
    # split the content into sections basded on the header "x.x.x"
    section_iter = re.finditer(r"^(\d+\.\d+\.\d+)\s+.*$", content, re.MULTILINE)
    sections = []
    for match in section_iter:
        sections.append({
            "start": match.start(),
            "number": match.group(1)
        })

    results = []
    for i in range(len(sections)):
        # get section content
        section_start = sections[i]["start"]
        section_end = sections[i+1]["start"] if i<len(sections)-1 else len(content)
        section_number = sections[i]["number"]
        section_content = content[section_start:section_end].strip()

        # find all images in the section
        image_iter = re.finditer(r"!\[\]\((.*)\)", section_content, re.MULTILINE) # ![](xxx/xxx/xxx.jpg)
        for match in image_iter:
            image_path = match.group(1)
            image_start = match.start()
            image_context = section_content[:image_start] # the content before the image are the context
            results.append(
                {
                    "section_number": section_number,
                    "context": image_context,
                    "image_path": image_path
                 }
            )
    return results

def test_get_context_with_image_path():
    with open("backend/process_pdfs/test.md", "r", encoding="utf-8") as f:
        content = f.read()
    results = get_context_with_image_path(content)
    print(results[0])

if __name__ == "__main__":
    test_get_context_with_image_path()