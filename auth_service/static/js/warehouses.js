document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        // Перенаправляем на страницу логина, если токен отсутствует
        window.location.href = '/login';
        return;
    }

    initializeWarehouses();

    // Открытие модального окна создания нового склада
    document.querySelector("#add-new-warehouse-btn").addEventListener("click", openAddWarehouseModal);

    // Обработчик для создания нового склада
    document.getElementById("add-warehouse-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        await createWarehouse();
    });

    // Обработчик для редактирования склада
    document.getElementById("edit-warehouse-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const warehouseId = document.getElementById("edit-warehouse-id").value;
        await updateWarehouse(warehouseId);
    });

    // Добавляем обработчик для кнопок "Редактировать" и "Удалить" в таблице
    document.getElementById("warehouses-table").addEventListener("click", (event) => {
        const target = event.target;
        const warehouseId = target.dataset.id;

        if (target.classList.contains("btn-warning")) {
            openEditWarehouseModal(warehouseId);
        } else if (target.classList.contains("btn-danger")) {
            const confirmed = confirm("Вы уверены, что хотите удалить склад?");
            if (confirmed) deleteWarehouse(warehouseId);
        }
    });
});

// Открытие модального окна для добавления нового склада
function openAddWarehouseModal() {
    document.getElementById("add-warehouse-form").reset();
    $("#addWarehouseModal").modal("show");
}

// Открытие модального окна для редактирования склада
async function openEditWarehouseModal(warehouseId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const warehouse = await response.json();

    // Заполняем поля формы редактирования данными склада
    document.getElementById("edit-warehouse-id").value = warehouse.warehouse_id;
    document.getElementById("edit-location").value = warehouse.location;
    document.getElementById("edit-manager-name").value = warehouse.manager_name || "";
    document.getElementById("edit-capacity").value = warehouse.capacity;
    document.getElementById("edit-current-stock").value = warehouse.current_stock || 0;
    document.getElementById("edit-contact-number").value = warehouse.contact_number || "";
    document.getElementById("edit-email").value = warehouse.email || "";
    document.getElementById("edit-is-active").value = warehouse.is_active ? "active" : "inactive";
    document.getElementById("edit-area-size").value = warehouse.area_size || "";

    // Открываем модальное окно для редактирования
    $("#editWarehouseModal").modal("show");
}

//Получение токена из базы данных
async function getTokenFromDatabase() {
    const userId = localStorage.getItem("user_id");
    const response = await fetch(`/get-user-token/${userId}`, {
        headers: { "Content-Type": "application/json" }
    });

    const data = await response.json();
    const token = data.access_token;
    const expiresAt = new Date(data.expires_at);

    // Проверяем истечение срока действия токена
    if (new Date() >= expiresAt) {
        console.log("Token expired. Redirecting to login page.");
        window.location.href = '/login';
        return null;
    }

    return token;
}

// Инициализация складов с использованием токена
async function initializeWarehouses() {
    const token = await getTokenFromDatabase();
    await loadWarehouses(token);
}

// Загрузка складов
async function loadWarehouses(token) {
    const response = await fetch("http://localhost:8002/warehouses/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const warehouses = await response.json();
    renderWarehousesTable(warehouses);
}

// Создание склада
async function createWarehouse() {
    const token = await getTokenFromDatabase();
    const warehouseData = {
        location: document.getElementById("add-location").value.trim(),
        manager_name: document.getElementById("add-manager-name").value.trim(),
        capacity: parseInt(document.getElementById("add-capacity").value.trim()),
        current_stock: parseInt(document.getElementById("add-current-stock").value.trim()) || 0,
        contact_number: document.getElementById("add-contact-number").value.trim(),
        email: document.getElementById("add-email").value.trim(),
        is_active: document.getElementById("add-is-active").value === "active",
        area_size: parseFloat(document.getElementById("add-area-size").value.trim()) || null,
    };

    await fetch("http://localhost:8002/warehouses/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(warehouseData)
    });

    document.getElementById("add-warehouse-form").reset();
    loadWarehouses(token);
    $("#addWarehouseModal").modal("hide");
}

// Обновление склада
async function updateWarehouse(warehouseId) {
    const token = await getTokenFromDatabase();
    const warehouseData = {
        location: document.getElementById("edit-location").value.trim(),
        manager_name: document.getElementById("edit-manager-name").value.trim(),
        capacity: parseInt(document.getElementById("edit-capacity").value.trim()),
        current_stock: parseInt(document.getElementById("edit-current-stock").value.trim()),
        contact_number: document.getElementById("edit-contact-number").value.trim(),
        email: document.getElementById("edit-email").value.trim(),
        is_active: document.getElementById("edit-is-active").value === "active",
        area_size: parseFloat(document.getElementById("edit-area-size").value.trim()) || null,
    };

    await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(warehouseData)
    });

    // Закрываем модальное окно и обновляем список складов
    $("#editWarehouseModal").modal("hide");
    loadWarehouses(token);
}

// Удаление склада
async function deleteWarehouse(warehouseId) {
    const token = await getTokenFromDatabase();
    await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    loadWarehouses(token);
}

// Заполнение таблицы складов
function renderWarehousesTable(warehouses) {
    const tableBody = document.querySelector("#warehouses-table tbody");
    tableBody.innerHTML = "";

    warehouses.forEach((warehouse) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${warehouse.location}</td>
            <td>${warehouse.manager_name || ""}</td>
            <td>${warehouse.capacity}</td>
            <td>${warehouse.current_stock || 0}</td>
            <td>${warehouse.is_active ? "Активен" : "Неактивен"}</td>
            <td>${warehouse.area_size || ""}</td>
            <td>
                <button class="btn btn-sm btn-warning" data-id="${warehouse.warehouse_id}">Редактировать</button>
                <button class="btn btn-sm btn-danger" data-id="${warehouse.warehouse_id}">Удалить</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}