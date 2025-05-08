from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64
import os
from typing import Literal

def get_Ollama_model(
        task: Literal["summarize_image", "chat"],
        num_ctx=32768, # Sets the size of the context window used to generate the next token. (Default: 2048)
        num_predict=-1, # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)
        temperature=0.5, # The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)
        top_k=40, # Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative. (Default: 40)
        top_p=0.8, # Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)
        repeat_penalty=1.2,
        seed=420
) -> ChatOllama:
    
    if task == "summarize_image":
        model = "llama3.2-vision:11b"
    else:
        model = "llama3.1:8b"

    llm = ChatOllama(
        model=model,
        num_ctx=num_ctx,
        num_predict=num_predict,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        seed=seed
    )

    return llm

def summarize_images_with_context(context: str, image_path: str) -> str:
    """Summarize the image using vision llm with context

    Args:
        contextt (str): context of the image
        image_path (str): image path

    Returns:
        the summarization of the image
    """
    
    def encode_image_base64(image_path: str) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片不存在: {image_path}")
        
        with open(image_path, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode('utf-8')
        return img_str
    # convert image to base64
    image_base64 = encode_image_base64(image_path)

    # get vision llm
    llm = get_Ollama_model(task="summarize_image")
    
    # Create mutimodal message
    system_message = SystemMessage(content="You are an expert in image summarization. \
                                   Please provide an accurate and detailed summary based on the given context \
                                   and image information.")
    human_message = HumanMessage(
        content=[
            {"type": "text", "text": context},
            {
                "type": "image", 
                "source_type": "base64",
                "data": image_base64, 
                "mime_type": "image/jpg"
            }
        ]
    )

    # get summary
    response = llm.invoke([system_message, human_message])
    return response.content

if __name__ == "__main__":
    context = "This is a image from the manual: \
                IAC Manual v9 - 10.2 Fallback procedure for ACC. \
                The context is: 10.2.2 Airfield Department is responsible for the management, \
                system provision and operation procedure of the fallback centre. \
                Latest update of the equipment list and redundancy level shall be referred to Airfield Department. \
                The equipment list at the fallback centre are as follow \
                (the locations of systems at the fallback centre is shown in Illustration 1-2):"
    image_path = "backend/data/extracted/IAC/images/5b44925af0e0d7ac75f2ef7343d20b52e4e38a639a33653649891f208b67c9de.jpg"

    summary = summarize_images_with_context(context=context, image_path=image_path)
    print(summary)