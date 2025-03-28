//chat.js
const chatListEl = document.getElementById('chat-list');
const chatContainerEl = document.getElementById('chat-container');
const chatTitleEl = document.getElementById('chat-title');
const chatMessagesEl = document.getElementById('chat-messages');
const loadHistoryBtn = document.getElementById('load-history-btn');
const messageInputEl = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

const userNamesCache = {};

const userId = localStorage.getItem("user_id");

let currentChatId = null;
let currentChatWebSocket = null;

let token = null;

// 1. При загрузке страницы запрашиваем список чатов
document.addEventListener('DOMContentLoaded', async () => {
    const token = await getTokenFromDatabase();

    if (!token) {
        console.error("Токен недействителен, перенаправление на страницу логина");
        window.location.href = "/login";
        return;
    }
    await fetchChats(token);
});



// Функция запроса списка чатов (REST GET /chats/)
async function fetchChats(token) {
    try {
        const response = await fetch('http://localhost:8004/chats/', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        if (!response.ok) {
            console.log('Ошибка при получении чатов', response.status);
            return;
        }
        const chats = await response.json();
        renderChatList(chats);
    } catch (err) {
        console.error('Ошибка fetchChats', err);
    }
}

// Отображение списка чатов
function renderChatList(chats) {
    chatListEl.innerHTML = '';
    chats.forEach(chat => {
        const li = document.createElement('li');
        li.classList.add('list-group-item', 'chat-list-item');
        li.textContent = chat.name || 'Без названия';

        li.addEventListener('click', () => {
            // Отмечаем активный элемент
            document.querySelectorAll('.chat-list-item.active')
                .forEach(el => el.classList.remove('active'));
            li.classList.add('active');

            openChat(chat.id, chat.name);
        });

        chatListEl.appendChild(li);
    });
}

// Функция открытия чата
async function openChat(chatId, chatName) {
    currentChatId = chatId;
    chatTitleEl.textContent = chatName || 'Без названия';
    chatMessagesEl.innerHTML = '';
    chatContainerEl.style.display = 'block';

    // Если был старый WebSocket — закрываем
    if (currentChatWebSocket) {
        currentChatWebSocket.close();
    }

    // Подключаемся к WS
    // Предположим, user_id мы где-то храним, например, в токене или localStorage
    // Сейчас для примера возьмем userId из "payload" токена или заранее захардкожено
    const wsUrl = `ws://localhost:8004/ws/${chatId}/${userId}`;
    currentChatWebSocket = new WebSocket(wsUrl);

    currentChatWebSocket.onopen = () => {
        console.log(`WS connected to chat ${chatId}`);
    };

    currentChatWebSocket.onmessage = (event) => {
        // Пришло новое сообщение (старое или новое) в формате JSON
        const messageObj = JSON.parse(event.data);
        addMessageToChat(messageObj);
    };

    currentChatWebSocket.onclose = () => {
        console.log('WS closed');
        currentChatWebSocket = null;
    };
}

// Добавить сообщение в DOM
// messageObj = { id, chat_id, sender_id, content, created_at, ... }
function addMessageToChat(messageObj) {
    const isOutgoing = (messageObj.sender_id === userId);
    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('message-bubble', isOutgoing ? 'outgoing' : 'incoming');

    const dateString = new Date(messageObj.created_at).toLocaleString();
    const senderName = messageObj.sender_name || (isOutgoing ? 'Вы' : `User ${messageObj.sender_id}`);

    bubbleDiv.innerHTML = `
      <div>${messageObj.content}</div>
      <div class="message-info">
        <strong>${senderName}</strong>, ${dateString}
      </div>
    `;
    chatMessagesEl.appendChild(bubbleDiv);

    // Автопрокрутка в самый низ
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

// При клике "Показать историю" — запрос к REST GET /chats/{chat_id}/messages
loadHistoryBtn.addEventListener('click', async () => {
    if (!currentChatId) return;
    try {
        const response = await fetch(`http://localhost:8004/chats/${currentChatId}/messages`, {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        if (!response.ok) {
            console.log('Ошибка при получении истории', response.status);
            return;
        }
        const allMessages = await response.json();
        // Очищаем окно чата и добавляем все сообщения заново
        chatMessagesEl.innerHTML = '';
        allMessages.forEach(msg => {
            // Тут формат данных MsgResponse, нужно добавить sender_id, content, created_at
            // У тебя в схеме: {id, chat_id, sender_id, content, created_at}
            // Но если sender_id нет — придётся доделать
            const messageObj = {
                id: msg.id,
                chat_id: msg.chat_id,
                sender_id: msg.sender_id || '???',
                content: msg.content,
                created_at: msg.created_at
            };
            addMessageToChat(messageObj);
        });
    } catch (err) {
        console.error('Ошибка loadHistory', err);
    }
});

// Отправка нового сообщения
sendBtn.addEventListener('click', () => {
    sendMessage();
});
messageInputEl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    if (!currentChatWebSocket) {
        alert('WebSocket не подключен');
        return;
    }
    const text = messageInputEl.value.trim();
    if (!text) return;

    // Отправляем JSON
    const payload = JSON.stringify({ content: text });
    currentChatWebSocket.send(payload);

    // Очищаем инпут
    messageInputEl.value = '';
}

async function fetchUserNameById(userId) {
    if (!userId) return null;
    // Если есть в кэше — берём из него
    if (userNamesCache[userId]) {
        return userNamesCache[userId];
    }
    try {
        const response = await fetch(`/user_name/${userId}`);
        if (!response.ok) {
            console.log("Не удалось получить имя для", userId, response.status);
            return userId; // fallback: вернём сам userId
        }
        const data = await response.json();
        userNamesCache[userId] = data.name;  // кэшируем
        return data.name;
    } catch (err) {
        console.error("Ошибка fetchUserNameById", err);
        return userId;
    }
}