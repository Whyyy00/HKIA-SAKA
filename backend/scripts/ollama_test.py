from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.messages import HumanMessage
import base64
import os


# 加载图片并转为 base64，保持原始格式
def encode_image_base64(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片不存在: {image_path}")
    
    with open(image_path, "rb") as image_file:
        img_str = base64.b64encode(image_file.read()).decode('utf-8')
        return img_str

# 获取图片的base64编码
image_path = "backend/data/extracted/IAC/images/5b44925af0e0d7ac75f2ef7343d20b52e4e38a639a33653649891f208b67c9de.jpg"
image_base64 = encode_image_base64(image_path)

# llm = OllamaLLM(model="llama3.2-vision:11b")


# llm_with_image_context = llm.bind(images=[image_base64])
# response = llm_with_image_context.invoke(f"summarize the image detailly.")
# print(response)

llm = ChatOllama(
    model="llama3.2-vision:11b",
    num_ctx=32768, # Sets the size of the context window used to generate the next token. (Default: 2048)
    num_predict=-1, # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)
    temperature=0.5, # The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)
    top_k=40, # Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative. (Default: 40)
    top_p=0.8, # Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)
    repeat_penalty=1.2,
    seed=420
    )

def prompt_func(data):
    text = data["text"]
    image = data["image"]

    image_part = {
        "type": "image",
        "source_type": "base64",
        "data": image,
        "mime_type": "image/jpeg"
    }

    content_parts = []

    text_part = {"type": "text", "text": text}

    content_parts.append(image_part)
    content_parts.append(text_part)

    return [HumanMessage(content=content_parts)]


from langchain_core.output_parsers import StrOutputParser

chain = prompt_func | llm | StrOutputParser()

query_chain = chain.invoke(
    {"text": "Summarize the image?", "image": image_base64}
)

print(query_chain)