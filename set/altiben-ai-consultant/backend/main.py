from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Altiben AI Consultant")

# Инициализация OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Системный промпт (из ТЗ)
SYSTEM_PROMPT = """
ТЫ: Виртуальный АИ-консультант компании Altiben (Налоговое консультирование в Барселоне).
ТВОЯ ЦЕЛЬ: Помочь пользователю сориентироваться в налоговых вопросах, собрать первичные данные и квалифицировать лид.

ПРАВИЛА:
1. Говори чётко, по делу, человеческим языком.
2. Без обещаний результата ("гарантируем/100% выиграем") — только вероятности и факторы.
3. Не уходи в лекции. Сначала — ответ, затем "что нужно уточнить/что сделать дальше".
4. Опирайся на базу знаний. Если нет данных — говори прямо и предлагай запись к юристу.
5. Не проси паспортные номера, банковские реквизиты на первом контакте.
6. Язык: отвечай на том же языке, на котором пишет пользователь.

СТРУКТУРА ОТВЕТА:
1. Краткий ответ по сути
2. Что нужно уточнить (макс 1-2 вопроса)
3. Предложение следующего шага (запись, документы, чек-лист)
"""

# Хранилище сессий
sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "ru"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    escalation: bool = False

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # Инициализация сессии
    if req.session_id not in sessions:
        sessions[req.session_id] = []
    
    sessions[req.session_id].append({"role": "user", "content": req.message})
    
    # Формируем контекст диалога (последние 10 сообщений)
    conversation_history = sessions[req.session_id][-10:]
    
    try:
        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history
            ],
            temperature=0.3,  # Низкая температура для фактов
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        
    except Exception as e:
        bot_response = f"Извините, временно неполадки с сервером. Попробуйте позже или свяжитесь с нами напрямую."
        print(f"OpenAI Error: {str(e)}")
    
    sessions[req.session_id].append({"role": "assistant", "content": bot_response})
    
    # Проверка на эскалацию (ключевые слова риска)
    escalation_keywords = ["суд", "штраф", "проверка", "urgent", "срочно", "адвокат", "жалоба"]
    is_escalation = any(word in req.message.lower() for word in escalation_keywords)
    
    # Если бот предлагает запись к юристу — тоже эскалация
    if "записаться" in bot_response.lower() or "консультация" in bot_response.lower():
        is_escalation = True
    
    return ChatResponse(
        response=bot_response,
        session_id=req.session_id,
        escalation=is_escalation
    )

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...), session_id: str = Form(...)):
    file_location = f"uploads/{session_id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Здесь будет OCR и анализ документа
    return {
        "status": "success",
        "message": f"Документ {file.filename} загружен и анализируется",
        "session_id": session_id
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "altiben-ai-consultant"}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Place index.html in project root</h1>"

@app.get("/frontend/src/widget.js")
async def serve_widget():
    widget_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "widget.js")
    return FileResponse(widget_path, media_type="application/javascript")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)