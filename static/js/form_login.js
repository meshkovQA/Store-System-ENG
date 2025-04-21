document.addEventListener('DOMContentLoaded', function () {

    localStorage.removeItem('access_token');
    console.log('Token deleted from localStorage');


    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        document.getElementById('emailError').style.display = 'none';
        document.getElementById('passwordError').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';

        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            valid = false;
        }

        if (password.length < 8) {
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        if (valid) {
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
                        localStorage.setItem('access_token', data.access_token);
                        console.log('Токен сохранен:', data.access_token);

                        loadStorePage(data.access_token);
                    } else {
                        document.getElementById('errorMessage').style.display = 'block';
                        if (data.detail === "Invalid email or password") {
                            document.getElementById('errorMessage').innerText = "Email or password is incorrect.";
                        } else {
                            document.getElementById('errorMessage').innerText = "Error: " + data.detail;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Error: " + error);
                });
        } else {
            document.getElementById('errorMessage').style.display = 'block';
        }
    });
});

function loadStorePage(token) {
    fetch('/store', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                console.error('Authentication error:', response.status);
                window.location.href = '/login';
            }
        })
        .then(html => {

            document.documentElement.innerHTML = html;
        })
        .catch(error => console.error('Error loading store page:', error));
}