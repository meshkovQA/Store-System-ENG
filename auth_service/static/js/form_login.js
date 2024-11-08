// login.js
document.addEventListener('DOMContentLoaded', function () {

    // Проверяем наличие refresh_token в cookies
    const refreshToken = getCookie('refresh_token');
    if (refreshToken) {
        // Если refresh_token найден, пытаемся получить новый access_token
        fetch('/refresh-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        })
            .then(response => response.json())
            .then(data => {
                if (data.access_token) {
                    // Переход на страницу /products
                    window.location.href = '/products';
                }
            })
            .catch(error => console.error('Error refreshing token:', error));
    }

    // Если пользователь заполняет форму логина
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        })
            .then(response => response.json())
            .then(data => {
                if (data.access_token) {
                    // Сохраняем токен и user_id в localStorage
                    localStorage.setItem('user_id', data.user_id);

                    // Если выбран "Запомнить меня", сохраняем refresh_token в Cookies
                    if (rememberMe) {
                        document.cookie = `refresh_token=${data.refresh_token}; path=/; max-age=${60 * 60 * 24 * 7};`;
                    }

                    // Переход на страницу /products
                    window.location.href = '/products';
                } else {
                    alert("Login failed: " + data.detail);
                }
            })
            .catch(error => console.error('Login error:', error));
    });
});

// Функция для получения значения cookie по имени
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}