//user_list.js
// function to get the list of users
function getUserList() {
    let token = localStorage.getItem('access_token');  // get token from localStorage

    if (!token) {
        console.error('Token not found');
        window.location.href = '/login';  // redirect to login page if token is not found
        return;
    }

    // API request to get the list of users
    fetch('/users/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,  // get token from localStorage
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.json();  // get json data
            } else {
                throw new Error('Error fetching user list: ' + response.statusText);
            }
        })
        .then(data => {
            // render the user table with the data received from the server
            renderUserTable(data.users);  // data.users — list of users
        })
        .catch(error => {
            console.error('Error:', error);
            window.location.href = '/login';  // if error occurs, redirect to login page
        });
}

// function to render the user table
function renderUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    userTableBody.innerHTML = '';  // clear the table body
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.is_superadmin ? 'super-admin' : 'user'}</td>
            <td>${!user.is_superadmin ? '<button class="btn btn-sm btn-success">Promote to superadmin</button>' : ''}</td>
        `;
        userTableBody.appendChild(row);
    });
}

// search functionality
// add event listener to the search input
document.getElementById('search').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const rows = document.querySelectorAll('#userTableBody tr');

    rows.forEach(row => {
        const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const email = row.querySelector('td:nth-child(3)').textContent.toLowerCase();

        if (name.includes(searchValue) || email.includes(searchValue)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

// upload list of users
document.addEventListener('DOMContentLoaded', function () {
    getUserList();
});