document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        window.location.href = '/login';
        return;
    }

    initializeWarehouses();

    document.querySelector("#add-new-warehouse-btn").addEventListener("click", openAddWarehouseModal);

    document.getElementById("add-warehouse-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        await createWarehouse();
    });

    document.getElementById("edit-warehouse-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const warehouseId = document.getElementById("edit-warehouse-id").value;
        await updateWarehouse(warehouseId);
    });

    document.getElementById("warehouses-table").addEventListener("click", (event) => {
        const target = event.target;
        const warehouseId = target.getAttribute("data-id");

        if (target.classList.contains("btn-outline-info")) {
            openViewWarehouseModal(warehouseId);
        } else if (target.classList.contains("btn-outline-warning")) {
            openEditWarehouseModal(warehouseId);
        } else if (target.classList.contains("btn-outline-danger")) {
            const confirmed = confirm("Are you sure you want to delete this warehouse?");
            if (confirmed) deleteWarehouse(warehouseId);
        }
    });
});

async function openViewWarehouseModal(warehouseId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const warehouse = await response.json();

    document.getElementById("view-warehouse-id").value = warehouse.warehouse_id;
    document.getElementById("view-location").value = warehouse.location;
    document.getElementById("view-manager-name").value = warehouse.manager_name || "";
    document.getElementById("view-capacity").value = warehouse.capacity;
    document.getElementById("view-current-stock").value = warehouse.current_stock || 0;
    document.getElementById("view-contact-number").value = warehouse.contact_number || "";
    document.getElementById("view-email").value = warehouse.email || "";
    document.getElementById("view-is-active").value = warehouse.is_active ? "Active" : "Inactive";
    document.getElementById("view-area-size").value = warehouse.area_size || "";

    $("#viewWarehouseModal").modal("show");
}

function openAddWarehouseModal() {
    document.getElementById("add-warehouse-form").reset();
    $("#addWarehouseModal").modal("show");
}

async function openEditWarehouseModal(warehouseId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const warehouse = await response.json();

    document.getElementById("edit-warehouse-id").value = warehouse.warehouse_id;
    document.getElementById("edit-location").value = warehouse.location;
    document.getElementById("edit-manager-name").value = warehouse.manager_name || "";
    document.getElementById("edit-capacity").value = warehouse.capacity;
    document.getElementById("edit-current-stock").value = warehouse.current_stock || 0;
    document.getElementById("edit-contact-number").value = warehouse.contact_number || "";
    document.getElementById("edit-email").value = warehouse.email || "";
    document.getElementById("edit-is-active").value = warehouse.is_active ? "Active" : "Inactive";
    document.getElementById("edit-area-size").value = warehouse.area_size || "";

    $("#editWarehouseModal").modal("show");
}

async function initializeWarehouses() {
    const token = await getTokenFromDatabase();
    await loadWarehouses(token);
}

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

    $("#editWarehouseModal").modal("hide");
    loadWarehouses(token);
}

async function deleteWarehouse(warehouseId) {
    const token = await getTokenFromDatabase();
    await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    loadWarehouses(token);
}

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
            <td>${warehouse.is_active ? "Active" : "Inactive"}</td>
            <td>${warehouse.area_size || ""}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-info" data-id="${warehouse.warehouse_id}">View</button>
                <button class="btn btn-sm btn-outline-warning" data-id="${warehouse.warehouse_id}">Edit</button>
                <button class="btn btn-sm btn-outline-danger" data-id="${warehouse.warehouse_id}">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function viewWarehouseProducts() {
    const warehouseId = document.getElementById("view-warehouse-id").value;
    window.open(`/warehouses_detail/${warehouseId}`, '_blank');
}