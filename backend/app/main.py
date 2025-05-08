import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import StreamingResponse
from backend.app.llm.rag_query import rag_query
import json
import time

app = FastAPI()

@app.post("/rag-chat")
async def rag_chat(request: Request):
    data = await request.json()
    query = data.get("query")
    
    if not query:
        return {"error": "query is required"}

    stream_iter, img_paths = rag_query(query)

    def event_stream():
        try:
            for chunk in stream_iter:
                yield f"data: {chunk}\n\n"
                time.sleep(0.01)
            # Send images path in the end
            if img_paths:
                yield f"data: __IMAGES__{json.dumps(img_paths)}\n\n"
        except Exception as e:
            yield f"data: [ERROR]: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)