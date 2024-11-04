document.addEventListener("DOMContentLoaded", function () {
    initializeSuppliers();

    document.getElementById("create-supplier-form-modal").addEventListener("submit", async (event) => {
        event.preventDefault();

        const token = await getTokenFromDatabase();

        const name = document.getElementById("name").value.trim();
        const contact_name = document.getElementById("contact_name").value.trim();
        const contact_email = document.getElementById("contact_email").value.trim();
        const phone_number = document.getElementById("phone_number").value.trim();
        const address = document.getElementById("address").value.trim();
        const country = document.getElementById("country").value.trim();
        const city = document.getElementById("city").value.trim();
        const website = document.getElementById("website").value.trim();

        if (name.length < 3 || name.length > 100) {
            alert("Название должно быть от 3 до 100 символов.");
            return;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(contact_email)) {
            alert("Введите корректный email.");
            return;
        }

        await fetch("http://localhost:8002/suppliers/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ name, contact_name, contact_email, phone_number, address, country, city, website })
        });

        document.getElementById("create-supplier-form-modal").reset();
        loadSuppliers(token);
        $("#addSupplierModal").modal("hide");
    });
});

async function initializeSuppliers() {
    const token = await getTokenFromDatabase();
    await loadSuppliers(token);
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
    renderSuppliersTable(suppliers);
}

async function searchSupplier() {
    const token = await getTokenFromDatabase();
    const searchQuery = document.getElementById("search-name").value.trim();

    const response = await fetch(`http://localhost:8002/suppliers?name=${searchQuery}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.ok) {
        const suppliers = await response.json();
        renderSuppliersTable(suppliers);
    } else {
        console.error("Ошибка при поиске поставщика:", response.status);
    }
}

function renderSuppliersTable(suppliers) {
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
                <button class="btn btn-sm btn-warning" data-id="${supplier.id}">Edit</button>
                <button class="btn btn-sm btn-danger" data-id="${supplier.id}">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

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

document.querySelector("#suppliers-table").addEventListener("click", async (event) => {
    if (event.target.classList.contains("btn-warning")) {
        const supplierId = event.target.dataset.id;
        openEditModal(supplierId);
    } else if (event.target.classList.contains("btn-danger")) {
        const supplierId = event.target.dataset.id;
        const confirmed = confirm("Вы уверены, что хотите удалить поставщика?");
        if (confirmed) {
            await deleteSupplier(supplierId);
        }
    }
});

async function deleteSupplier(supplierId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.ok) {
        loadSuppliers(token); // Перезагружаем список поставщиков после удаления
    } else {
        console.error("Ошибка при удалении поставщика:", response.status);
    }
}

async function openEditModal(supplierId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Ошибка при загрузке данных поставщика для редактирования:", response.status);
        return;
    }

    const supplier = await response.json();

    // Заполняем поля модального окна редактирования
    document.getElementById("name").value = supplier.name;
    document.getElementById("contact_name").value = supplier.contact_name;
    document.getElementById("contact_email").value = supplier.contact_email;
    document.getElementById("phone_number").value = supplier.phone_number;
    document.getElementById("address").value = supplier.address;
    document.getElementById("country").value = supplier.country;
    document.getElementById("city").value = supplier.city;
    document.getElementById("website").value = supplier.website;

    // Открываем модальное окно для редактирования
    $("#addSupplierModal").modal("show");

    // Обновляем обработчик для сохранения изменений
    document.getElementById("create-supplier-form-modal").onsubmit = async (event) => {
        event.preventDefault();
        await updateSupplier(supplierId);
    };
}

async function updateSupplier(supplierId) {
    const token = await getTokenFromDatabase();

    const name = document.getElementById("name").value.trim();
    const contact_name = document.getElementById("contact_name").value.trim();
    const contact_email = document.getElementById("contact_email").value.trim();
    const phone_number = document.getElementById("phone_number").value.trim();
    const address = document.getElementById("address").value.trim();
    const country = document.getElementById("country").value.trim();
    const city = document.getElementById("city").value.trim();
    const website = document.getElementById("website").value.trim();

    const response = await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ name, contact_name, contact_email, phone_number, address, country, city, website })
    });

    if (response.ok) {
        $("#addSupplierModal").modal("hide"); // Закрываем модальное окно после успешного обновления
        loadSuppliers(token); // Обновляем список поставщиков
    } else {
        console.error("Ошибка при обновлении поставщика:", response.status);
    }
}