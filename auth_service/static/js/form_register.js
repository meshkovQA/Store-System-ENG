document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('registerForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let username = document.getElementById('username').value;
        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        function resetError(elementId) {
            const errorElement = document.getElementById(elementId);
            errorElement.style.display = 'none';
            errorElement.innerText = '';
        }

        function showError(elementId, message) {
            const errorElement = document.getElementById(elementId);
            errorElement.innerText = message;
            errorElement.style.display = 'block';
        }

        resetError('usernameError');
        resetError('emailError');
        resetError('passwordError');
        document.getElementById('successMessage').style.display = 'none';

        const sqlScriptPattern = /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|SCRIPT|<script|alert|onload|onerror)\b)/i;
        if (username.trim() === "" || /^\s/.test(username)) {
            showError('usernameError', "Name must not contain only spaces or start with a space.");
            valid = false;
        } else if (username.length < 3 || username.length > 50) {
            showError('usernameError', "Name must be between 3 and 50 characters.");
            valid = false;
        } else if (sqlScriptPattern.test(username)) {
            showError('usernameError', "Name contains invalid characters.");
            valid = false;
        }

        let emailPattern = /^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            showError('emailError', "Email is not valid.");
            valid = false;
        }
        if (password.trim() === "" || /^\s/.test(password)) {
            showError('passwordError', "Password must not contain only spaces or start with a space.");
            valid = false;
        } else if (password.length < 8) {
            showError('passwordError', "Password must be more than 8 characters.");
            valid = false;
        }

        if (password.length < 8) {
            document.getElementById('passwordError').innerText = "Password must be more than 8 characters.";
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        if (valid) {
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
                        const successMessage = document.getElementById('successMessage');
                        successMessage.style.display = 'block';

                        setTimeout(() => {
                            window.location.href = "/login";
                        }, 3000);
                    } else {
                        return response.json().then(data => {
                            if (data.detail === "Email already registered") {
                                document.getElementById('emailError').innerText = "This email is already registered.";
                                document.getElementById('emailError').style.display = 'block';
                            } else if (data.detail === "Invalid email format.") {
                                document.getElementById('emailError').innerText = "Email field contains invalid characters.";
                                document.getElementById('emailError').style.display = 'block';
                            } else if (data.detail === "Name contains invalid characters.") {
                                document.getElementById('usernameError').innerText = "Mane must not contain only spaces or start with a space.";
                                document.getElementById('usernameError').style.display = 'block';
                            } else if (data.detail === "Password contains invalid characters.") {
                                document.getElementById('passwordError').innerText = "Password must not contain only spaces or start with a space.";
                                document.getElementById('passwordError').style.display = 'block';
                            } else {
                                alert("Error: " + data.detail);
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Error: " + error);
                });
        }
    });
});

