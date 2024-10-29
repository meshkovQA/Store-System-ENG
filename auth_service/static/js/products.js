document.addEventListener("DOMContentLoaded", function () {
    loadProducts();

    document.getElementById("create-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const name = document.getElementById("name").value;
        const description = document.getElementById("description").value;
        const category = document.getElementById("category").value;
        const price = parseFloat(document.getElementById("price").value);
        const stock_quantity = parseInt(document.getElementById("stock_quantity").value);
        const supplier_name = document.getElementById("supplier_name").value;

        // Отправка запроса на сервер для создания продукта
        await fetch("http://products_service:8002/products/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({
                name, description, category, price, stock_quantity, supplier_name
            })
        });

        // Закрытие модального окна и перезагрузка списка продуктов
        document.getElementById("create-product-form").reset();
        const modal = new bootstrap.Modal(document.getElementById("addProductModal"));
        modal.hide();
        loadProducts();
    });
});

async function loadProducts() {
    const response = await fetch("http://products_service:8002/products/", {
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
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