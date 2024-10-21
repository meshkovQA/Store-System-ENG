//user_list.js
// Функция для получения списка пользователей с API
function getUserList() {
    let token = localStorage.getItem('access_token');  // Получаем токен из localStorage

    if (!token) {
        console.error('Токен не найден. Перенаправляем на страницу логина.');
        window.location.href = '/login';  // Перенаправляем на логин, если токена нет
        return;
    }

    // Делаем запрос на API для получения списка пользователей
    fetch('/users/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,  // Передаем токен в заголовке Authorization
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.json();  // Получаем JSON с данными пользователей
            } else {
                throw new Error('Ошибка получения списка пользователей');
            }
        })
        .then(data => {
            // Рендерим таблицу с пользователями
            renderUserTable(data.users);  // data.users — это массив пользователей, который возвращает сервер
        })
        .catch(error => {
            console.error('Ошибка:', error);
            window.location.href = '/login';  // Если произошла ошибка, перенаправляем на логин
        });
}

// Функция для рендеринга таблицы пользователей
function renderUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    userTableBody.innerHTML = '';  // Очищаем таблицу перед добавлением новых данных

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.is_superadmin ? 'супер-админ' : 'пользователь'}</td>
            <td>${!user.is_superadmin ? '<button class="btn btn-sm btn-success">Повысить до супер-админа</button>' : ''}</td>
        `;
        userTableBody.appendChild(row);
    });
}

// Поиск по таблице пользователей
document.getElementById('search').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const rows = document.querySelectorAll('#userTableBody tr');

    rows.forEach(row => {
        const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const email = row.querySelector('td:nth-child(3)').textContent.toLowerCase();

        if (name.includes(searchValue) || email.includes(searchValue)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

// Загружаем список пользователей при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    getUserList();
});