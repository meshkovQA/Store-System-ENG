//user_list.js
function getUserList() {
    let token = localStorage.getItem('access_token');

    if (!token) {
        console.error('Token not found');
        window.location.href = '/login';
        return;
    }

    fetch('/users/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error fetching user list');
            }
        })
        .then(data => {
            renderUserTable(data.users);
        })
        .catch(error => {
            console.error('Error:', error);
            window.location.href = '/login';
        });
}

function renderUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    userTableBody.innerHTML = '';
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.is_superadmin ? 'superadmin' : 'user'}</td>
            <td>${!user.is_superadmin ? '<button class="btn btn-sm btn-success">Promote to superadmin</button>' : ''}</td>
        `;
        userTableBody.appendChild(row);
    });
}

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

document.addEventListener('DOMContentLoaded', function () {
    getUserList();
});