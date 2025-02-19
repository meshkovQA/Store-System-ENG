// check_superadmin.js

document.addEventListener("DOMContentLoaded", async function () {
    const token = await getTokenFromDatabase();

    try {
        const response = await fetch("/check-superadmin", {
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Failed to fetch admin status");
        }

        const data = await response.json();

        if (data.is_superadmin) {
            document.getElementById("user-list-item").style.display = "block";
            document.getElementById("pending-approval-item").style.display = "block";
            document.getElementById("adminOrdersBtn").style.display = "inline-block";
        }
    } catch (error) {
        console.error("Error checking super admin status:", error);
    }
});
