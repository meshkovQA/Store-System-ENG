//user_list.js
// Объявляем переменные для списка всех пользователей и количества пользователей на странице
let allUsers = [];
const usersPerPage = 10;

// Загружаем токен и получаем список пользователей при загрузке страницы
document.addEventListener("DOMContentLoaded", async function () {
    console.log("Page loaded, starting token retrieval...");
    const token = await getTokenFromDatabase();

    if (!token) {
        console.log("No token found, redirecting to login page.");
        // Перенаправляем на страницу логина, если токен отсутствует
        window.location.href = '/login';
        return;
    }
    else {
        console.log("Token retrieved successfully, loading user list...");
        getUserList(token);
    }
});


// Функция для получения списка пользователей с API
function getUserList(token) {
    console.log("Fetching user list with provided token:", token);
    fetch('/users/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            console.log("User list response status:", response.status);
            return response.json();  // Получаем JSON с данными пользователей
        })
        .then(data => {
            console.log("User list data:", data);  // Лог данных
            if (Array.isArray(data)) {
                allUsers = data;  // Сохраняем всех пользователей
                renderUserTable(allUsers.slice(0, usersPerPage));  // Показываем первую страницу
                renderPagination(Math.ceil(allUsers.length / usersPerPage));
            } else {
                console.error("User list is not in expected format");
            }
        })
        .catch(error => {
            console.error("Error fetching user list:", error);
            //window.location.href = '/login';
        });
}

// Функция для рендеринга таблицы пользователей
function renderUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    if (!userTableBody) {
        console.error("Error: userTableBody element not found on the page.");
        return;
    }

    userTableBody.innerHTML = '';  // Очищаем таблицу перед добавлением новых данных

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
        <td>${user.id}</td>
        <td>${user.name}</td>
        <td>${user.email}</td>
        <td>${user.role === 'superadmin' ? 'супер-админ' : 'пользователь'}</td>
        <td>${user.role !== 'superadmin' ? `<button class="btn btn-sm btn-success promote-btn" data-id="${user.id}">Повысить до супер-админа</button>` : ''}</td>
    `;
        userTableBody.appendChild(row);
    });
    console.log("User table rendered successfully.");

    // Добавляем обработчик для всех кнопок "Повысить до супер-админа"
    document.querySelectorAll(".promote-btn").forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.getAttribute("data-id");
            promoteUserToSuperadmin(userId);
        });
    });
}

// Функция для рендеринга элементов управления страницей
function renderPagination(totalPages) {
    const paginationContainer = document.getElementById('paginationContainer');
    paginationContainer.innerHTML = '';

    for (let page = 1; page <= totalPages; page++) {
        const pageItem = document.createElement('li');
        pageItem.className = 'page-item';
        pageItem.innerHTML = `<a class="page-link" href="#">${page}</a>`;

        pageItem.addEventListener('click', (e) => {
            e.preventDefault();
            const start = (page - 1) * usersPerPage;
            const end = start + usersPerPage;
            renderUserTable(allUsers.slice(start, end));
        });

        paginationContainer.appendChild(pageItem);
    }
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

// Функция для повышения пользователя до супер-админа
async function promoteUserToSuperadmin(userId) {
    const token = await getTokenFromDatabase();
    fetch(`/users/promote/${userId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert("User successfully promoted to super admin.");
                getUserList(token);  // Обновляем список пользователей после повышения
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail);
                });
            }
        })
        .catch(error => {
            console.error("Error promoting user:", error);
            alert("Error promoting user: " + error.message);
        });
}