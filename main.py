from ollama import chat
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class Message(BaseModel):
    input: str
    cur: int

class Response(BaseModel):
    response: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)
def stream_chat(cur, messages):
    stream = chat(
        model='llama3.2',
        messages=messages,
        stream=True,
    )
    ai_message = ''
    for chunk in stream:
        if not chunk['done']:
            ai_message += chunk['message']['content']
            yield chunk['message']['content']
        else:
            ai_message += '\n'
            list_list[cur].append({
                "role": "assistant",
                "content": ai_message
            })
            for sublist in list_list:
                print(sublist)
            yield '\n'

list_list = [[]]
list_list[0].append({
                "role": "assistant",
                "content": "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" 
            })
chat_data_list = []
@app.post("/clear/")
async def clear(message: Message):
    cur=message.cur
    print(cur)
    list_list[cur].clear()
    list_list[cur].append({
                "role": "assistant",
                "content": "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" 
            })
    return

@app.post("/del/")
async def delete(message: Message):
    cur=message.cur
    del list_list[cur]
    return list_list[cur]

@app.get("/newChat/")
async def newChat():
    list_list.append([{
                "role": "assistant",
                "content": "😸💖主人好喵！我是猫娘小助手喵💖，我会很可爱地回答你的问题喵💕" 
            }])
    return
    
@app.post("/view/")
async def view(message: Message):
    cur = message.cur
    return list_list[cur] # 返回当前节点的对话记录

@app.post("/aichat/")
async def get_response(message: Message):
    user_message = message.input
    cur = message.cur
    print(cur)
    list_list[cur].append({
        "role": "user",
        "content": user_message
    })
    return StreamingResponse(stream_chat(cur, list_list[cur]), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)