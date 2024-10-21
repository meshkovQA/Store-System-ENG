document.addEventListener('DOMContentLoaded', function () {

    localStorage.removeItem('access_token');
    console.log('Токен удален при посещении страницы логина.');


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
                    if (data.access_token) {
                        // Сохраняем токен в localStorage
                        localStorage.setItem('access_token', data.access_token);
                        console.log('Токен сохранен:', data.access_token);

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

// Функция для загрузки страницы store
function loadStorePage(token) {
    // Запрашиваем страницу /store с токеном в заголовке
    fetch('/store', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.text();  // Получаем HTML страницы
            } else {
                console.error('Ошибка авторизации на странице /store', response.status);
                window.location.href = '/login';  // Перенаправляем на логин, если нет доступа
            }
        })
        .then(html => {
            // Вставляем содержимое страницы store в текущий DOM
            document.documentElement.innerHTML = html;
        })
        .catch(error => console.error('Ошибка при загрузке страницы /store:', error));
}