// Altiben AI Consultant Widget
(function() {
  const API_URL = 'http://localhost:8000';
  
  function createWidget() {
    const widgetHTML = `
      <div id="altiben-widget-container">
        <button id="altiben-toggle-btn">💬 Altiben AI</button>
        <div id="altiben-chat-window" style="display:none;">
          <div class="chat-header">
            <h3>Altiben Assistant</h3>
            <button id="altiben-close-btn">✕</button>
          </div>
          <div id="altiben-messages"></div>
          <div class="chat-input">
            <input type="text" id="altiben-input" placeholder="Ваш вопрос...">
            <button id="altiben-send-btn">➤</button>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', widgetHTML);
    
    // Стили
    const styles = `
      #altiben-widget-container { position: fixed; bottom: 20px; right: 20px; z-index: 9999; }
      #altiben-toggle-btn { background: #0066cc; color: white; border: none; padding: 15px 20px; border-radius: 50px; cursor: pointer; font-size: 16px; }
      #altiben-chat-window { width: 350px; height: 500px; background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); display: flex; flex-direction: column; }
      .chat-header { background: #0066cc; color: white; padding: 15px; border-radius: 10px 10px 0 0; display: flex; justify-content: space-between; }
      #altiben-messages { flex: 1; padding: 15px; overflow-y: auto; }
      .chat-input { display: flex; padding: 10px; border-top: 1px solid #eee; }
      #altiben-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
      #altiben-send-btn { background: #0066cc; color: white; border: none; padding: 10px 15px; margin-left: 5px; border-radius: 5px; cursor: pointer; }
      .msg { margin: 10px 0; padding: 10px; border-radius: 5px; max-width: 80%; }
      .msg.user { background: #e3f2fd; margin-left: auto; }
      .msg.ai { background: #f5f5f5; }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
    
    // Логика
    const toggleBtn = document.getElementById('altiben-toggle-btn');
    const closeBtn = document.getElementById('altiben-close-btn');
    const chatWindow = document.getElementById('altiben-chat-window');
    const sendBtn = document.getElementById('altiben-send-btn');
    const input = document.getElementById('altiben-input');
    const messagesDiv = document.getElementById('altiben-messages');
    
    let sessionId = localStorage.getItem('altiben_session') || 'session_' + Date.now();
    localStorage.setItem('altiben_session', sessionId);
    
    toggleBtn.onclick = () => chatWindow.style.display = 'flex';
    closeBtn.onclick = () => chatWindow.style.display = 'none';
    
    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      
      // Добавляем сообщение пользователя
      messagesDiv.innerHTML += `<div class="msg user">${text}</div>`;
      input.value = '';
      
      // Отправка на сервер
      try {
        const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, message: text, language: 'ru' })
        });
        const data = await response.json();
        
        // Добавляем ответ бота
        messagesDiv.innerHTML += `<div class="msg ai">${data.response}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      } catch (error) {
        messagesDiv.innerHTML += `<div class="msg ai">Ошибка соединения с сервером</div>`;
      }
    }
    
    sendBtn.onclick = sendMessage;
    input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
  }
  
  // Инициализация после загрузки страницы
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidget);
  } else {
    createWidget();
  }
})();