// login.js
document.addEventListener('DOMContentLoaded', function () {

    const refreshToken = getCookie('refresh_token');
    if (refreshToken) {
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
                    window.location.href = '/products';
                }
            })
            .catch(error => console.error('Error refreshing token:', error));
    }

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
                    localStorage.setItem('user_id', data.user_id);

                    if (rememberMe) {
                        document.cookie = `refresh_token=${data.refresh_token}; path=/; max-age=${60 * 60 * 24 * 7};`;
                    }

                    window.location.href = '/products';
                } else {
                    alert("Login failed: " + data.detail);
                }
            })
            .catch(error => console.error('Login error:', error));
    });
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}