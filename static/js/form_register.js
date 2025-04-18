document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('registerForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let username = document.getElementById('username').value;
        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        // Hide error messages
        document.getElementById('successMessage').style.display = 'none';
        document.getElementById('usernameError').style.display = 'none';
        document.getElementById('emailError').style.display = 'none';
        document.getElementById('passwordError').style.display = 'none';

        // Validation of username
        if (username.length < 3 || username.length > 60) {
            document.getElementById('usernameError').style.display = 'block';
            valid = false;
        }

        // Validation of email
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            valid = false;
        }

        // Validation of password
        if (password.length < 6) {
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        // If username, email and password are valid
        if (valid) {
            // send POST request to /register/
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
                        // if registration is successful, show success message
                        window.location.href = "/login";
                    } else {
                        return response.json().then(data => {
                            // if registration fails, show error message
                            if (data.detail === "Email already registered") {
                                document.getElementById('emailError').innerText = "This email is already registered";
                                document.getElementById('emailError').style.display = 'block';
                            } else {
                                alert("Registration failed: " + data.detail);
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

