# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
import uuid

app = FastAPI()

# Инициализация моделей и БД
llm = ChatOpenAI(model="gpt-4o", temperature=0.3) # Низкая температура для фактов
vector_store = Pinecone.from_existing_index("altiben-kb", embedding_model)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 1. Поиск в базе знаний (RAG)
    docs = vector_store.similarity_search(req.message, k=3)
    context = "\n".join([d.page_content for d in docs])
    
    # 2. Формирование промпта с контекстом
    system_prompt = load_system_prompt() # Загрузка промпта из раздела 2
    full_prompt = f"{system_prompt}\n\nКонтекст из базы знаний:\n{context}\n\nИстория диалога: {get_history(req.session_id)}\n\nПользователь: {req.message}"
    
    # 3. Генерация ответа
    response = llm.predict(full_prompt)
    
    # 4. Проверка на эскалацию (ключевые слова риска)
    if check_risk_keywords(response):
        create_lead_ticket(req.session_id, req.message, "High Risk/Escalation")
        
    save_history(req.session_id, req.message, response)
    return {"response": response, "session_id": req.session_id}

@app.post("/upload-document")
async def upload_doc(file: UploadFile = File(...), session_id: str = Form(...)):
    # Обработка документов (OCR + Text Extraction)
    text_content = await parse_document(file) # Используем PyPDF2 или Tesseract
    
    # Сохраняем в векторную базу временной сессии пользователя
    vector_store.add_texts([text_content], metadatas={"session": session_id, "type": "user_doc"})
    
    return {"status": "Document analyzed", "summary": "Документ принят и проанализирован."}

@app.post("/video-stream-analysis")
async def analyze_video_stream(session_id: str, video_data: bytes):
    # Отправка кадров в GPT-4 Vision или специализированную модель
    # Возвращает текстовое описание ситуации для дальнейшего диалога
    analysis = await vision_model.analyze(video_data)
    return {"analysis": analysis}