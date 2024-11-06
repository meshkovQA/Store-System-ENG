// login.js
document.addEventListener('DOMContentLoaded', function () {
    localStorage.removeItem('user_id');
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

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

                    // Переход на страницу /products
                    window.location.href = '/products';
                } else {
                    alert("Login failed: " + data.detail);
                }
            })
            .catch(error => console.error('Login error:', error));
    });
});