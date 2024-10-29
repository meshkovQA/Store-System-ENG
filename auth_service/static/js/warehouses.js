document.addEventListener("DOMContentLoaded", function () {
    loadWarehouses();

    document.getElementById("create-warehouse-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const location = document.getElementById("location").value;
        const manager_name = document.getElementById("manager_name").value;
        const capacity = parseInt(document.getElementById("capacity").value);
        const current_stock = parseInt(document.getElementById("current_stock").value);
        const contact_number = document.getElementById("contact_number").value;
        const email = document.getElementById("email").value;
        const is_active = document.getElementById("is_active").value === "true";
        const area_size = parseFloat(document.getElementById("area_size").value);

        await fetch("http://products_service:8002/warehouses/", {  // URL сервиса складов
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({
                location, manager_name, capacity, current_stock,
                contact_number, email, is_active, area_size
            })
        });
        loadWarehouses();
    });
});

async function loadWarehouses() {
    const response = await fetch("http://products_service:8002/warehouses/", {  // URL сервиса складов
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
    const warehouses = await response.json();
    const tableBody = document.querySelector("#warehouses-table tbody");
    tableBody.innerHTML = "";

    warehouses.forEach((warehouse) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${warehouse.location}</td>
            <td>${warehouse.manager_name}</td>
            <td>${warehouse.capacity}</td>
            <td>${warehouse.current_stock}</td>
            <td>${warehouse.contact_number}</td>
            <td>${warehouse.email}</td>
            <td>${warehouse.is_active ? "Активен" : "Неактивен"}</td>
            <td>${warehouse.area_size}</td>
            <td>${new Date(warehouse.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-warning">Edit</button>
                <button class="btn btn-sm btn-danger">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}