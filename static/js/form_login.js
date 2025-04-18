document.addEventListener('DOMContentLoaded', function () {

    localStorage.removeItem('access_token');
    console.log('Token deleted from localStorage');


    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        let email = document.getElementById('email').value;
        let password = document.getElementById('password').value;
        let valid = true;

        // hide error messages
        document.getElementById('emailError').style.display = 'none';
        document.getElementById('passwordError').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';

        // Validation of email
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            valid = false;
        }

        // Validation of password
        if (password.length < 8) {
            document.getElementById('passwordError').style.display = 'block';
            valid = false;
        }

        // if email and password are valid
        if (valid) {
            // send POST request to /login/
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
                        // save the token in localStorage
                        localStorage.setItem('access_token', data.access_token);
                        console.log('Token saved to localStorage:', data.access_token);

                        // redirect to /store
                        loadStorePage(data.access_token);
                    } else {
                        // show error message
                        document.getElementById('errorMessage').style.display = 'block';
                        if (data.detail === "Invalid email or password") {
                            document.getElementById('errorMessage').innerText = "password or email is incorrect";
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

// function to load the /store page
function loadStorePage(token) {
    // assign the token to the Authorization header
    fetch('/store', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.text();  // get html content
            } else {
                console.error('Error loading /store:', response.statusText);
                window.location.href = '/login';  // redirect to login page if unauthorized
            }
        })
        .then(html => {
            // paste the html content into the current document
            document.documentElement.innerHTML = html;
        })
        .catch(error => console.error('Error loading /store:', error));
}