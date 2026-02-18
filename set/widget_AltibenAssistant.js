// widget/AltibenAssistant.js
import React, { useState, useRef } from 'react';

const AltibenAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const sessionId = useRef(localStorage.getItem('altiben_session') || generateUUID());

  // Функция отправки сообщения
  const sendMessage = async (text, type = 'text') => {
    const newMsg = { text, sender: 'user', type };
    setMessages(prev => [...prev, newMsg]);

    const response = await fetch('https://api.altiben.com/chat', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId.current, message: text })
    });
    const data = await response.json();
    
    setMessages(prev => [...prev, { text: data.response, sender: 'ai' }]);
    
    // Голосовой вывод (TTS)
    if (data.response) speakText(data.response);
  };

  // Голосовой ввод (Web Speech API)
  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window)) return alert("Браузер не поддерживает голос");
    
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-ES'; // Авто-определение лучше делать на бэкенде
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      sendMessage(transcript, 'voice');
    };
    recognition.start();
    setIsRecording(true);
  };

  // Загрузка документов
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId.current);
    
    fetch('https://api.altiben.com/upload-document', { method: 'POST', body: formData })
      .then(res => res.json())
      .then(data => sendMessage(`Я загрузил документ: ${file.name}. Проанализируйте его.`));
  };

  return (
    <div className="altiben-widget">
      {!isOpen && (
        <button onClick={() => setIsOpen(true)} className="fab">
          💬 Консультант Altiben
        </button>
      )}
      
      {isOpen && (
        <div className="chat-window">
          <div className="header">
            <h3>Altiben AI Assistant</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.sender}`}>{m.text}</div>
            ))}
          </div>

          <div className="controls">
            <input type="file" onChange={handleFileUpload} id="doc-upload" hidden />
            <label htmlFor="doc-upload" className="icon-btn">📎</label>
            <button onClick={toggleVoice} className={isRecording ? "recording" : ""}>🎤</button>
            <input type="text" placeholder="Ваш вопрос..." onKeyPress={(e) => e.key === 'Enter' && sendMessage(e.target.value)} />
          </div>
        </div>
      )}
    </div>
  );
};