document.addEventListener("DOMContentLoaded", function () {
    initialize();

    document.getElementById("create-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        // Получаем токен из базы данных
        const token = await getTokenFromDatabase();

        const name = document.getElementById("name").value;
        const description = document.getElementById("description").value;
        const category = document.getElementById("category").value;
        const price = parseFloat(document.getElementById("price").value);
        const stock_quantity = parseInt(document.getElementById("stock_quantity").value);
        const supplier_id = document.getElementById("supplier_id").value;

        await fetch("http://localhost:8002/products/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                name, description, category, price, stock_quantity, supplier_id
            })
        });

        document.getElementById("create-product-form").reset();
        const modal = new bootstrap.Modal(document.getElementById("addProductModal"));
        modal.hide();
        loadProducts(token);
    });
});

async function initialize() {
    const token = await getTokenFromDatabase();
    await loadProducts(token);
    await loadSuppliers(token);
}

// Функция для получения токена из базы данных
async function getTokenFromDatabase() {
    const userId = localStorage.getItem("user_id"); // Извлекаем текущий ID пользователя из localStorage

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

async function loadProducts(token) {
    const response = await fetch("http://localhost:8002/products/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Ошибка при загрузке продуктов:", response.status);
        return;
    }

    const products = await response.json();
    const tableBody = document.querySelector("#products-table tbody");
    tableBody.innerHTML = "";

    products.forEach((product) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${product.name}</td>
            <td>${product.description}</td>
            <td>${product.category}</td>
            <td>${product.price}</td>
            <td>
                <button class="btn btn-sm btn-warning">Edit</button>
                <button class="btn btn-sm btn-danger">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
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
    const supplierSelect = document.getElementById("supplier_id");

    supplierSelect.innerHTML = "";
    suppliers.forEach((supplier) => {
        const option = document.createElement("option");
        option.value = supplier.supplier_id;
        option.text = supplier.name;
        supplierSelect.appendChild(option);
    });
}