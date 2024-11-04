document.addEventListener('DOMContentLoaded', function () {

    localStorage.removeItem('user_id');
    console.log('id пользователя удален при посещении страницы логина.');


    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        // Сброс сообщений об ошибках
        document.getElementById('emailError').style.display = 'none';
        document.getElementById('passwordError').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';

        // Валидация email
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            valid = false;
        }

        // Валидация пароля
        if (password.length < 8) {
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        // Если все корректно
        if (valid) {
            // Отправка данных на сервер через fetch
            fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.user_id) {
                        // Сохраняем токен в localStorage
                        localStorage.setItem('user_id', data.user_id);
                        console.log('User ID сохранен:', data.user_id);

                        // Перенаправляем на страницу store
                        loadStorePage(data.access_token);
                    } else {
                        // Обработка ошибок логина
                        document.getElementById('errorMessage').style.display = 'block';
                        if (data.detail === "Invalid email or password") {
                            document.getElementById('errorMessage').innerText = "Неверный email или пароль.";
                        } else {
                            document.getElementById('errorMessage').innerText = "Ошибка при авторизации.";
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Ошибка при отправке данных");
                });
        } else {
            document.getElementById('errorMessage').style.display = 'block';
        }
    });
});

// Функция для загрузки страницы store с актуальным токеном из базы данных
async function loadStorePage() {
    const userId = localStorage.getItem("user_id");

    if (!userId) {
        window.location.href = '/login';
        return;
    }

    try {
        // Запрашиваем актуальный токен для пользователя из базы данных
        const tokenResponse = await fetch(`/get-user-token/${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!tokenResponse.ok) {
            console.error("Ошибка при получении токена:", tokenResponse.status);
            window.location.href = '/login';
            return;
        }

        const tokenData = await tokenResponse.json();
        const token = tokenData.access_token;

        // Используем полученный токен для запроса страницы store
        const storeResponse = await fetch('/store', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (storeResponse.ok) {
            const html = await storeResponse.text();
            document.documentElement.innerHTML = html; // Вставляем HTML страницы store в текущий DOM
        } else {
            console.error("Ошибка авторизации на странице /store:", storeResponse.status);
            window.location.href = '/login';
        }
    } catch (error) {
        console.error("Ошибка при загрузке страницы /store:", error);
        window.location.href = '/login';
    }
}