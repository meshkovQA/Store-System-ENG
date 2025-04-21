document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        window.location.href = '/login';
        return;
    }

    const warehouseId = getWarehouseIdFromUrl();

    if (!warehouseId) {
        alert("ID of the warehouse not found in URL");
        return;
    }

    loadWarehouseInfo(warehouseId);
    loadProducts(warehouseId);

    document.getElementById("add-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        await addProductToWarehouse(warehouseId);
    });
});

function getWarehouseIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.pathname);
    const pathParts = window.location.pathname.split("/");
    return pathParts[pathParts.length - 1];
}

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

    document.querySelector("h2").textContent = `Warehouse: ${warehouse.location}`;
    document.getElementById("warehouse-manager-name").textContent = warehouse.manager_name || 'None';
    document.getElementById("warehouse-capacity").textContent = warehouse.capacity;
    document.getElementById("warehouse-current-stock").textContent = warehouse.current_stock || 0;
    document.getElementById("warehouse-contact-number").textContent = warehouse.contact_number || 'None';
    document.getElementById("warehouse-email").textContent = warehouse.email || 'None';
    document.getElementById("warehouse-is-active").textContent = warehouse.is_active ? "Active" : "Inactive";
    document.getElementById("warehouse-area-size").textContent = warehouse.area_size || 'None';
}

async function loadProducts(warehouseId, page = 1) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/productinwarehouses/${warehouseId}?page=${page}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.status === 404) {
        document.querySelector("#products-table tbody").innerHTML = `
            <tr><td colspan="4" class="text-center">This warehouse has no products.</td></tr>
        `;
        document.getElementById("pagination").innerHTML = "";
        return;
    }

    if (!response.ok) {
        alert("Error loading products");
        return;
    }

    const data = await response.json();
    renderProductsTable(data.products);
    renderPagination(data.total_pages, page);
}

function renderProductsTable(products) {
    const tableBody = document.querySelector("#products-table tbody");
    tableBody.innerHTML = "";

    products.forEach((product) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.name}</td>
            <td>${product.quantity}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="openEditProductModal('${product.product_warehouse_id}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct('${product.product_warehouse_id}')">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}


function openAddProductModal() {
    document.getElementById("add-product-form").reset();
    $("#addProductModal").modal("show");
}

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

    if (response.ok) {
        alert("Product successfully added to warehouse");
        loadProducts();
        $("#addProductModal").modal("hide");
    } else {
        alert("Error adding product to warehouse");
    }
}

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

function openEditProductModal(productWarehouseId) {
    const quantity = prompt("Enter new quantity for the product:");
    if (quantity && quantity > 0) {
        updateProductQuantity(productWarehouseId, parseInt(quantity));
    }
}

async function updateProductQuantity(productWarehouseId, quantity) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/productinwarehouses/${productWarehouseId}`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ quantity })
    });

    if (response.ok) {
        alert("Quantity successfully updated");
        loadProducts();
    } else {
        alert("Error updating quantity");
    }
}

async function deleteProduct(productWarehouseId) {
    const confirmed = confirm("Are you sure you want to delete this product from the warehouse?");
    if (!confirmed) return;

    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/productinwarehouses/${productWarehouseId}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.ok) {
        alert("Product successfully deleted from warehouse");
        loadProducts();
    } else {
        alert("Error deleting product from warehouse");
    }
}

