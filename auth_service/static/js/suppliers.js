document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        // Перенаправляем на страницу логина, если токен отсутствует
        window.location.href = '/login';
        return;
    }

    initializeSuppliers();

    // Открытие модального окна создания нового поставщика
    document.querySelector("#add-new-supplier-btn").addEventListener("click", openAddModal);

    // Обработчик для создания нового поставщика
    document.getElementById("add-supplier-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        await createSupplier();
    });

    // Обработчик для редактирования поставщика
    document.getElementById("edit-supplier-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const supplierId = document.getElementById("edit-supplier-id").value;
        await updateSupplier(supplierId);
    });

    // Добавляем обработчик для кнопок "Редактировать" и "Удалить" в таблице
    document.getElementById("suppliers-table").addEventListener("click", (event) => {
        const target = event.target;
        const supplierId = target.dataset.id;

        if (target.classList.contains("btn-outline-warning")) {
            openEditModal(supplierId);
        } else if (target.classList.contains("btn-outline-danger")) {
            const confirmed = confirm("Вы уверены, что хотите удалить поставщика?");
            if (confirmed) deleteSupplier(supplierId);
        }
    });
});

// Открытие модального окна для добавления нового поставщика
function openAddModal() {
    document.getElementById("add-supplier-form").reset();
    $("#addSupplierModal").modal("show");
}

// Открытие модального окна для редактирования поставщика
async function openEditModal(supplierId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const supplier = await response.json();

    // Заполняем поля формы редактирования данными поставщика
    document.getElementById("edit-supplier-id").value = supplier.supplier_id;
    document.getElementById("edit-name").value = supplier.name;
    document.getElementById("edit-contact_name").value = supplier.contact_name;
    document.getElementById("edit-contact_email").value = supplier.contact_email;
    document.getElementById("edit-phone_number").value = supplier.phone_number;
    document.getElementById("edit-address").value = supplier.address;
    document.getElementById("edit-country").value = supplier.country;
    document.getElementById("edit-city").value = supplier.city;
    document.getElementById("edit-website").value = supplier.website;

    // Открываем модальное окно для редактирования
    $("#editSupplierModal").modal("show");
}

//Использование токена для инициализации поставщиков
async function initializeSuppliers() {
    const token = await getTokenFromDatabase();
    await loadSuppliers(token);
}

//Загрузка поставщиков
async function loadSuppliers(token) {
    const response = await fetch("http://localhost:8002/suppliers/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const suppliers = await response.json();
    renderSuppliersTable(suppliers);
}

// Поиск поставщика
async function searchSupplier() {
    const token = await getTokenFromDatabase();
    const searchQuery = document.getElementById("search-name").value.trim();

    const response = await fetch(`http://localhost:8002/search_suppliers?name=${encodeURIComponent(searchQuery)}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.ok) {
        const suppliers = await response.json();
        console.log("Найденные поставщики:", suppliers); // Отладка: вывод найденных поставщиков в консоль
        renderSuppliersTable(suppliers);
    } else {
        console.error("Ошибка при поиске поставщика:", response.status);
    }
}

// Создание поставщика
async function createSupplier() {
    const token = await getTokenFromDatabase();
    const supplierData = {
        name: document.getElementById("add-name").value.trim(),
        contact_name: document.getElementById("add-contact_name").value.trim(),
        contact_email: document.getElementById("add-contact_email").value.trim(),
        phone_number: document.getElementById("add-phone_number").value.trim(),
        address: document.getElementById("add-address").value.trim(),
        country: document.getElementById("add-country").value.trim(),
        city: document.getElementById("add-city").value.trim(),
        website: document.getElementById("add-website").value.trim()
    };

    await fetch("http://localhost:8002/suppliers/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(supplierData)
    });

    document.getElementById("add-supplier-form").reset();
    loadSuppliers(token);
    $("#addSupplierModal").modal("hide");
}

// Обновление поставщика
async function updateSupplier(supplierId) {
    const token = await getTokenFromDatabase();
    const supplierData = {
        name: document.getElementById("edit-name").value.trim(),
        contact_name: document.getElementById("edit-contact_name").value.trim(),
        contact_email: document.getElementById("edit-contact_email").value.trim(),
        phone_number: document.getElementById("edit-phone_number").value.trim(),
        address: document.getElementById("edit-address").value.trim(),
        country: document.getElementById("edit-country").value.trim(),
        city: document.getElementById("edit-city").value.trim(),
        website: document.getElementById("edit-website").value.trim()
    };

    await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(supplierData)
    });

    // Закрываем модальное окно и обновляем список поставщиков
    $("#editSupplierModal").modal("hide");
    loadSuppliers(token);
}

//Удаление поставщика
async function deleteSupplier(supplierId) {
    const token = await getTokenFromDatabase();
    await fetch(`http://localhost:8002/suppliers/${supplierId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    loadSuppliers(token);
}

//Заполнение таблицы поставщиков
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
            <td class="text-center">
                <button class="btn btn-sm btn-outline-warning mt-2" data-id="${supplier.supplier_id}">Редактировать</button>
                <button class="btn btn-sm btn-outline-danger mt-2" data-id="${supplier.supplier_id}">Удалить</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}