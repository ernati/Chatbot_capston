#haystack
import os
import logging


# chatbot
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ela.chatbot import Chatbot
from typing import List



os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)



##put documents to es
#if you want test part of all files
chatbot = Chatbot(0)

# #else you want test all files
# chatbot = Chatbot(1)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Question(BaseModel):
    question: str = "..."


class ChatbotAnswer(BaseModel):
    answer: str = "..."
    score: float = "0.00"


def query_to_Question(ques: Question, qr: str):
    ques.question = qr

def QA_to_ChatbotAnswer(deli_list, res: dict):
    if len(res["answers"]) == 0 :
        return 0
    deli = ChatbotAnswer()
    if res["answers"][0].type == 'other':
        deli.answer = res["answers"][0].answer + " -FAQ- "
        deli.score = res["answers"][0].score
        deli_list.append(deli)
    else:  # "type" == extractive
        if len(res["answers"]) == 0:
            deli.answer = "no answer"
            deli_list.append(deli)
        else:
            for i in range( 0,len(res["answers"]) ):
                deli.answer = res["answers"][i].answer
                deli.score = res["answers"][i].score
                deli_list.append(deli)
                deli = ChatbotAnswer()


@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@app.get("/chatbot/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

# #test_on_web
# @app.post("/chatbot/", response_class=HTMLResponse)
# async def answer_question(request: Request):
#     # Let's say I received a question as a Question Instance.
#     form = await request.form()
#     query = form["query"]
#
#     # deliver_list = []
#     result = chatbot.Chatbot_pipeline(query)
#                                                                                                 #deliver_list[0].score
#     return templates.TemplateResponse("answer.html", {"request": request, "query": query, "score": " 0 ",
#                                                       "answers": result}) #[0].answer})

#for_frontend
@app.post("/chatbot/")
async def answer_question(thing : Question) -> List[ChatbotAnswer]:
    # Let's say I received a question as a Question Instance.

    query = thing.question

    # deliver_list = []
    result = chatbot.Chatbot_pipeline(query)
    result_fin = []

    for answer in result :
        temp = ChatbotAnswer()
        temp.answer = answer
        temp.score = 1.00
        result_fin.append(temp)

    return result_fin


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)
