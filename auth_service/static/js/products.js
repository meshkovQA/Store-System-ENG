//products.js
document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    if (!token) {
        return;
    }

    initializeProducts();

    document.querySelector("#add-new-product-btn").addEventListener("click", openAddProductModal);

    document.getElementById("add-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        document.getElementById("nameError").style.display = 'none';
        document.getElementById("descriptionError").style.display = 'none';
        document.getElementById("categoryError").style.display = 'none';
        document.getElementById("priceError").style.display = 'none';
        document.getElementById("stockQuantityError").style.display = 'none';
        document.getElementById("supplierError").style.display = 'none';
        document.getElementById("imageError").style.display = 'none';
        document.getElementById("weightError").style.display = 'none';
        document.getElementById("dimensionsError").style.display = 'none';
        document.getElementById("manufacturerError").style.display = 'none';

        let valid = true;

        let name = document.getElementById("add-name").value.trim();
        if (!/^[а-яА-Яa-zA-Z0-9\s]{3,100}$/.test(name)) {
            document.getElementById("nameError").style.display = 'block';
            valid = false;
        }

        let description = document.getElementById("add-description").value.trim();
        if (description.length > 500) {
            document.getElementById("descriptionError").style.display = 'block';
            valid = false;
        }

        let category = document.getElementById("add-category").value.trim();
        if (category && (category.length > 50 || !/^[а-яА-Яa-zA-Z0-9\s]*$/.test(category))) {
            document.getElementById("categoryError").style.display = 'block';
            valid = false;
        }


        let price = document.getElementById("add-price").value;
        if (!price || isNaN(price) || parseFloat(price) <= 0 || !/^\d+(\.\d{1,2})?$/.test(price) || price.length > 10) {
            document.getElementById("priceError").style.display = 'block';
            valid = false;
        }

        let stockQuantity = document.getElementById("add-stock-quantity").value;
        if (!/^\d+$/.test(stockQuantity) || parseInt(stockQuantity) < 0) {
            document.getElementById("stockQuantityError").style.display = 'block';
            valid = false;
        }

        let supplierId = document.getElementById("add-supplier-id").value;
        if (!supplierId) {
            document.getElementById("supplierError").style.display = 'block';
            valid = false;
        }

        let dimensions = document.getElementById("add-dimensions").value.trim();
        if (dimensions && !/^[\dx\s]{1,100}$/.test(dimensions)) {
            document.getElementById("dimensionsError").style.display = 'block';
            valid = false;
        }

        if (valid) {
            createProduct();
        }
    });
    document.getElementById("edit-product-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        if (validateProductForm("edit")) {
            const productId = document.getElementById("edit-product-id").value;
            await updateProduct(productId);
        }
    });

    document.getElementById("products-table").addEventListener("click", (event) => {
        const target = event.target;
        const productId = target.dataset.id;

        if (target.classList.contains("btn-outline-warning")) {
            openEditProductModal(productId);
        } else if (target.classList.contains("btn-outline-danger")) {
            const confirmed = confirm("Are you sure you want to delete this product?");
            if (confirmed) deleteProduct(productId);
        }
    });
});

function validateProductForm(formPrefix) {
    let isValid = true;
    let errorMessage = "";

    const name = document.getElementById(`${formPrefix}-name`).value.trim();
    const description = document.getElementById(`${formPrefix}-description`).value.trim();
    const supplierId = document.getElementById(`${formPrefix}-supplier-id`).value;
    const price = document.getElementById(`${formPrefix}-price`).value;
    const stockQuantity = document.getElementById(`${formPrefix}-stock-quantity`).value;
    const weight = document.getElementById(`${formPrefix}-weight`).value;

    if (!name) {
        errorMessage += "Name is required.\n";
        isValid = false;
    }
    if (!description) {
        errorMessage += "Description is required.\n";
        isValid = false;
    }
    if (!supplierId) {
        errorMessage += "Need to select a supplier.\n";
        isValid = false;
    }

    if (price && isNaN(parseFloat(price))) {
        errorMessage += "Price should be a number with up to 2 decimal places.\n";
        isValid = false;
    }
    if (stockQuantity && isNaN(parseInt(stockQuantity))) {
        errorMessage += "Quantity should be a positive integer.\n";
        isValid = false;
    }
    if (weight && isNaN(parseFloat(weight))) {
        errorMessage += "Weight should be a number.\n";
        isValid = false;
    }

    if (!supplierId || supplierId === "undefined") {
        alert("please select a supplier");
        return;
    }

    if (!isValid) {
        alert(errorMessage);
    }
    return isValid;
}

function openAddProductModal() {
    document.getElementById("add-product-form").reset();
    loadSuppliers("#add-supplier-id");
    $("#addProductModal").modal("show");
}

async function openEditProductModal(productId) {
    const token = await getTokenFromDatabase();
    const response = await fetch(`http://localhost:8002/products/${productId}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        console.error("Error loading product:", response.status);
        return;
    }

    const product = await response.json();

    document.getElementById("edit-product-id").value = product.product_id;
    document.getElementById("edit-name").value = product.name;
    document.getElementById("edit-description").value = product.description;
    document.getElementById("edit-category").value = product.category || "";
    document.getElementById("edit-price").value = product.price + " euro" || "";
    document.getElementById("edit-stock-quantity").value = product.stock_quantity || "";
    loadSuppliers("#edit-supplier-id", product.supplier_id);
    document.getElementById("edit-weight").value = product.weight + " kg" || "";
    document.getElementById("edit-dimensions").value = product.dimensions + " m" || "";
    document.getElementById("edit-manufacturer").value = product.manufacturer || "";

    $("#editProductModal").modal("show");
}

async function initializeProducts() {
    const token = await getTokenFromDatabase();
    await loadProducts(token);
}

async function loadProducts(token) {
    const response = await fetch("http://localhost:8002/products/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const products = await response.json();
    renderProductsTable(products);
}

async function createProduct() {
    const token = await getTokenFromDatabase();
    const supplierId = document.getElementById("add-supplier-id").value;
    console.log("Selected Supplier ID:", supplierId);

    const productData = {
        name: document.getElementById("add-name").value.trim(),
        description: document.getElementById("add-description").value.trim(),
        category: document.getElementById("add-category").value.trim(),
        price: parseFloat(document.getElementById("add-price").value) || null,
        stock_quantity: parseInt(document.getElementById("add-stock-quantity").value) || null,
        supplier_id: supplierId,
        weight: parseFloat(document.getElementById("add-weight").value) || null,
        dimensions: document.getElementById("add-dimensions").value.trim(),
        manufacturer: document.getElementById("add-manufacturer").value.trim(),
    };
    console.log("Supplier ID:", productData.supplier_id);

    await fetch("http://localhost:8002/products/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(productData)
    });

    document.getElementById("add-product-form").reset();
    loadProducts(token);
    $("#addProductModal").modal("hide");
}

async function updateProduct(productId) {
    const token = await getTokenFromDatabase();
    const productData = {
        name: document.getElementById("edit-name").value.trim(),
        description: document.getElementById("edit-description").value.trim(),
        category: document.getElementById("edit-category").value.trim(),
        price: parseFloat(document.getElementById("edit-price").value) || null,
        stock_quantity: parseInt(document.getElementById("edit-stock-quantity").value) || null,
        supplier_id: document.getElementById("edit-supplier-id").value,
        weight: parseFloat(document.getElementById("edit-weight").value) || null,
        dimensions: document.getElementById("edit-dimensions").value.trim(),
        manufacturer: document.getElementById("edit-manufacturer").value.trim(),
    };

    await fetch(`http://localhost:8002/products/${productId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(productData)
    });

    $("#editProductModal").modal("hide");
    loadProducts(token);
}

async function deleteProduct(productId) {
    const token = await getTokenFromDatabase();
    await fetch(`http://localhost:8002/products/${productId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    loadProducts(token);
}

function renderProductsTable(products) {
    const tableBody = document.querySelector("#products-table tbody");
    tableBody.innerHTML = "";

    products.forEach((product) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.name}</td>
            <td>${product.description}</td>
            <td>${product.category || ""}</td>
            <td>${product.price + " euro" || ""}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-warning mt-2" data-id="${product.product_id}">Edit</button>
                <button class="btn btn-sm btn-outline-danger mt-2" data-id="${product.product_id}">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function loadSuppliers(selectorId, selectedSupplierId = null) {
    const token = await getTokenFromDatabase();
    const response = await fetch("http://localhost:8002/suppliers/", {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    const suppliers = await response.json();
    const select = document.querySelector(selectorId);
    select.innerHTML = `<option value="" disabled selected>Choose a supplier</option>`;

    suppliers.forEach((supplier) => {
        const option = document.createElement("option");
        option.value = supplier.supplier_id;
        option.textContent = supplier.name;
        if (supplier.id === selectedSupplierId) option.selected = true;
        select.appendChild(option);
    });
    console.log("Supplier ID:", selectedSupplierId);
}

async function searchProduct() {
    const token = await getTokenFromDatabase();
    const searchQuery = document.getElementById("search-name").value.trim();

    const response = await fetch(`http://localhost:8002/search_products/?name=${encodeURIComponent(searchQuery)}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (response.ok) {
        const products = await response.json();
        renderProductsTable(products);
    } else {
        console.error("Error searching products:", response.status);
    }
}