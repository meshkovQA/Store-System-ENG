document.addEventListener("DOMContentLoaded", function () {
    loadSuppliers();

    document.getElementById("create-supplier-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const name = document.getElementById("name").value;
        const contact_name = document.getElementById("contact_name").value;
        const contact_email = document.getElementById("contact_email").value;
        const phone_number = document.getElementById("phone_number").value;
        const address = document.getElementById("address").value;
        const country = document.getElementById("country").value;
        const city = document.getElementById("city").value;
        const website = document.getElementById("website").value;

        await fetch("http://products_service:8002/suppliers/", {  // URL сервиса поставщиков
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({ name, contact_name, contact_email, phone_number, address, country, city, website })
        });
        loadSuppliers();
    });
});

async function loadSuppliers() {
    const response = await fetch("http://products_service:8002/suppliers/", {  // URL сервиса поставщиков
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
    const suppliers = await response.json();
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
                <button class="btn btn-sm btn-warning">Edit</button>
                <button class="btn btn-sm btn-danger">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}