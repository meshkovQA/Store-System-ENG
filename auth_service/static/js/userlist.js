//user_list.js
let allUsers = [];
const usersPerPage = 10;

document.addEventListener("DOMContentLoaded", async function () {
    console.log("Page loaded, starting token retrieval...");
    const token = await getTokenFromDatabase();

    if (!token) {
        console.log("No token found, redirecting to login page.");
        window.location.href = '/login';
        return;
    }
    else {
        console.log("Token retrieved successfully, loading user list...");
        getUserList(token);
    }
});


function getUserList(token) {
    console.log("Fetching user list with provided token:", token);
    fetch('/users/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            console.log("User list response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("User list data:", data);
            if (Array.isArray(data)) {
                allUsers = data;
                renderUserTable(allUsers.slice(0, usersPerPage));
                renderPagination(Math.ceil(allUsers.length / usersPerPage));
            } else {
                console.error("User list is not in expected format");
            }
        })
        .catch(error => {
            console.error("Error fetching user list:", error);
        });
}

function renderUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    if (!userTableBody) {
        console.error("Error: userTableBody element not found on the page.");
        return;
    }

    userTableBody.innerHTML = '';

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
        <td>${user.id}</td>
        <td>${user.name}</td>
        <td>${user.email}</td>
        <td>${user.role === 'superadmin' ? 'superadmin' : 'user'}</td>
        <td>${user.role !== 'superadmin' ? `<button class="btn btn-sm btn-success promote-btn" data-id="${user.id}">Promote to superadmin</button>` : ''}</td>
    `;
        userTableBody.appendChild(row);
    });
    console.log("User table rendered successfully.");

    document.querySelectorAll(".promote-btn").forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.getAttribute("data-id");
            promoteUserToSuperadmin(userId);
        });
    });
}

function renderPagination(totalPages) {
    const paginationContainer = document.getElementById('paginationContainer');
    paginationContainer.innerHTML = '';

    for (let page = 1; page <= totalPages; page++) {
        const pageItem = document.createElement('li');
        pageItem.className = 'page-item';
        pageItem.innerHTML = `<a class="page-link" href="#">${page}</a>`;

        pageItem.addEventListener('click', (e) => {
            e.preventDefault();
            const start = (page - 1) * usersPerPage;
            const end = start + usersPerPage;
            renderUserTable(allUsers.slice(start, end));
        });

        paginationContainer.appendChild(pageItem);
    }
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

async function promoteUserToSuperadmin(userId) {
    const token = await getTokenFromDatabase();
    fetch(`/users/promote/${userId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert("User successfully promoted to super admin.");
                getUserList(token);
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail);
                });
            }
        })
        .catch(error => {
            console.error("Error promoting user:", error);
            alert("Error promoting user: " + error.message);
        });
}