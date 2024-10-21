document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('registerForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let username = document.getElementById('username').value;
        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        // Сброс сообщений об ошибках и успехе
        document.getElementById('successMessage').style.display = 'none';
        document.getElementById('usernameError').style.display = 'none';
        document.getElementById('emailError').style.display = 'none';
        document.getElementById('passwordError').style.display = 'none';

        // Валидация имени пользователя
        if (username.length < 3 || username.length > 60) {
            document.getElementById('usernameError').style.display = 'block';
            valid = false;
        }

        // Валидация email
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            valid = false;
        }

        // Валидация пароля
        if (password.length < 6) {
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        // Если валидация успешна
        if (valid) {
            // Отправка данных на сервер через fetch
            fetch('/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: username,
                    email: email,
                    password: password
                })
            })
                .then(response => {
                    if (response.status === 201) {
                        // Если регистрация успешна, перенаправляем на страницу логина
                        window.location.href = "/login";
                    } else {
                        return response.json().then(data => {
                            // Если возникла ошибка, отображаем сообщение об ошибке
                            if (data.detail === "Email already registered") {
                                document.getElementById('emailError').innerText = "Этот email уже зарегистрирован.";
                                document.getElementById('emailError').style.display = 'block';
                            } else {
                                alert("Ошибка при регистрации");
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Ошибка при отправке данных");
                });
        }
    });
});

