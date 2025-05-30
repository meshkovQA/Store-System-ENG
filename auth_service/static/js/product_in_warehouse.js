// Инициализация загрузки продуктов
document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        // Перенаправляем на страницу логина, если токен отсутствует
        window.location.href = '/login';
        return;
    }

    const warehouseId = getWarehouseIdFromUrl();

    if (!warehouseId) {
        alert("ID of the warehouse not found in URL");
        return;
    }

    // Загрузка информации о складе
    loadWarehouseInfo(warehouseId);
    // Загрузка информации о продуктах на складе

    const products = await fetchProductsFromWarehouse(warehouseId, token);
    renderProductsTable(products);

    // Инициализация события для добавления продукта
    document.getElementById("add-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        await addProductToWarehouse(warehouseId);
    });
});

// Функция для извлечения warehouse_id из URL
function getWarehouseIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.pathname);
    const pathParts = window.location.pathname.split("/");
    return pathParts[pathParts.length - 1]; // Последний элемент пути
}

// Функция для загрузки информации о складе
async function loadWarehouseInfo(warehouseId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/warehouses/${warehouseId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        alert("Error loading warehouse information");
        return;
    }

    const warehouse = await response.json();

    // Отображение информации о складе на странице (если нужно обновить данные)
    document.querySelector("h2").textContent = `Склад: ${warehouse.location}`;
    document.getElementById("warehouse-manager-name").textContent = warehouse.manager_name || 'None';
    document.getElementById("warehouse-capacity").textContent = warehouse.capacity;
    document.getElementById("warehouse-current-stock").textContent = warehouse.current_stock || 0;
    document.getElementById("warehouse-contact-number").textContent = warehouse.contact_number || 'None';
    document.getElementById("warehouse-email").textContent = warehouse.email || 'None';
    document.getElementById("warehouse-is-active").textContent = warehouse.is_active ? "Active" : "Inactive";
    document.getElementById("warehouse-area-size").textContent = warehouse.area_size || 'None';
}

// ---- Получение продуктов со склада ----
async function fetchProductsFromWarehouse(warehouseId, token) {
    const response = await fetch(`http://localhost:8002/productinwarehouses/${warehouseId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Error fetching products from warehouse:", response.status);
        return [];
    }

    const productsInWarehouse = await response.json();
    console.log("Products in warehouse:", productsInWarehouse);

    const products = [];

    // Последовательно загружаем информацию о каждом продукте
    for (const productWarehouse of productsInWarehouse) {
        const productDetails = await fetchProductDetails(productWarehouse.product_id, token);
        if (productDetails) {
            products.push({
                ...productDetails,
                stock_quantity: productWarehouse.quantity, // Количество со склада
                product_warehouse_id: productWarehouse.product_warehouse_id
            });
        } else {
            console.warn("Cannot fetch details for product ID:", productWarehouse.product_id);
        }
    }

    console.log("all products in warehouse:", products);
    return products;
}

// ---- Получение деталей продукта ----
async function fetchProductDetails(productId, token) {
    const response = await fetch(`http://localhost:8002/products/${productId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Error fetching product details:", response.status);
        return null;
    }

    return await response.json();
}

// Заполнение таблицы продуктов
function renderProductsTable(products) {
    const tableBody = document.querySelector("#products-table tbody");
    tableBody.innerHTML = "";

    if (products.length === 0) {
        tableBody.innerHTML = `
            <tr><td colspan="4" class="text-center">This warehouse has no products.</td></tr>
        `;
        return;
    }

    products.forEach((product) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.name}</td>
            <td>${product.stock_quantity}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="openEditProductModal('${product.product_warehouse_id}', '${product.product_id}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct('${product.product_warehouse_id}', '${product.product_id}')">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}


// Открытие модального окна добавления продукта
function openAddProductModal() {
    document.getElementById("add-product-form").reset();
    $("#addProductModal").modal("show");
}

// Обработка добавления нового продукта
async function addProductToWarehouse(warehouseId) {
    const token = await getTokenFromDatabase();
    const productId = document.getElementById("product-id").value;
    const quantity = parseInt(document.getElementById("product-quantity").value);

    const response = await fetch(`http://localhost:8002/productinwarehouses?warehouse_id=${warehouseId}&product_id=${productId}&quantity=${quantity}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const result = await response.json();

    if (response.ok) {
        alert("Product successfully added to warehouse");
        const warehouseId = getWarehouseIdFromUrl();
        const products = await fetchProductsFromWarehouse(warehouseId, token);
        renderProductsTable(products);
        $("#addProductModal").modal("hide");
    } else {
        alert(`Error adding product: ${result.detail || "Unknown error"}`);
    }
}

// Пагинация
function renderPagination(totalPages, currentPage) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement("li");
        pageItem.className = "page-item" + (i === currentPage ? " active" : "");
        pageItem.innerHTML = `<a class="page-link" href="#" onclick="loadProducts(${i})">${i}</a>`;
        pagination.appendChild(pageItem);
    }
}

// Открытие модального окна для редактирования продукта
function openEditProductModal(productWarehouseId, productId) {
    const quantity = prompt("Enter new quantity:");
    if (quantity && quantity > 0) {
        updateProductQuantity(productWarehouseId, productId, parseInt(quantity));
    }
}

// Обновление количества продукта на складе
async function updateProductQuantity(productWarehouseId, productId, quantity) {
    const token = await getTokenFromDatabase();
    const url = `http://localhost:8002/productinwarehouses/${productId}?product_warehouse_id=${productWarehouseId}&quantity=${quantity}`;

    const response = await fetch(url, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const result = await response.json();

    if (response.ok) {
        alert("Quantity successfully updated");
        const warehouseId = getWarehouseIdFromUrl();
        const products = await fetchProductsFromWarehouse(warehouseId, token);
        renderProductsTable(products);
    } else {
        alert(`Error updating quantity: ${result.detail || "Unknown error"}`);
    }
}

// Удаление продукта со склада
async function deleteProduct(productWarehouseId, productId) {
    const confirmed = confirm("Are you sure you want to delete this product from the warehouse?");
    if (!confirmed) return;

    const token = await getTokenFromDatabase();
    const url = `http://localhost:8002/productinwarehouses/${productId}?product_warehouse_id=${productWarehouseId}`;

    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.ok) {
        alert("Product successfully deleted from warehouse");
        const warehouseId = getWarehouseIdFromUrl();
        const products = await fetchProductsFromWarehouse(warehouseId, token);
        renderProductsTable(products);
    } else if (response.status === 404) {
        alert("Product not found in warehouse");
    } else {
        alert("Error deleting product: " + (await response.json()).detail || "Unknown error");
    }
}

