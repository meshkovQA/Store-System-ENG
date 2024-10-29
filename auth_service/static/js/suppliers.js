document.addEventListener("DOMContentLoaded", function () {
    initializeSuppliers();

    document.getElementById("create-supplier-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        // Получаем токен из базы данных
        const token = await getTokenFromDatabase();

        const name = document.getElementById("name").value;
        const contact_name = document.getElementById("contact_name").value;
        const contact_email = document.getElementById("contact_email").value;
        const phone_number = document.getElementById("phone_number").value;
        const address = document.getElementById("address").value;
        const country = document.getElementById("country").value;
        const city = document.getElementById("city").value;
        const website = document.getElementById("website").value;

        await fetch("http://localhost:8002/suppliers/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ name, contact_name, contact_email, phone_number, address, country, city, website })
        });

        document.getElementById("create-supplier-form").reset();
        loadSuppliers(token);
    });
});

async function initializeSuppliers() {
    const token = await getTokenFromDatabase();
    await loadSuppliers(token);
}

// Функция для получения токена из базы данных
async function getTokenFromDatabase() {
    const userId = localStorage.getItem("user_id");

    if (!userId) {
        console.error("User ID не найден в localStorage. Перенаправление на страницу логина.");
        window.location.href = '/login';
        return null;
    }

    const response = await fetch(`/get-user-token/${userId}`, {
        headers: {
            "Content-Type": "application/json",
        }
    });

    if (!response.ok) {
        console.error("Ошибка при получении токена:", response.status);
        window.location.href = '/login';
        return null;
    }

    const data = await response.json();
    return data.access_token;
}

async function loadSuppliers(token) {
    const response = await fetch("http://localhost:8002/suppliers/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Ошибка при загрузке поставщиков:", response.status);
        return;
    }

    const suppliers = await response.json();
    const tableBody = document.querySelector("#suppliers-table tbody");
    tableBody.innerHTML = "";

    suppliers.forEach((supplier) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${supplier.name}</td>
            <td>${supplier.contact_name}</td>
            <td>${supplier.contact_email}</td>
            <td>${supplier.phone_number}</td>
            <td>${supplier.address}</td>
            <td>${supplier.country}</td>
            <td>${supplier.city}</td>
            <td>${supplier.website}</td>
            <td>
                <button class="btn btn-sm btn-warning">Edit</button>
                <button class="btn btn-sm btn-danger">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}