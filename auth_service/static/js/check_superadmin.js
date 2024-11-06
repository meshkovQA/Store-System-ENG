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
        }
    } catch (error) {
        console.error("Error checking super admin status:", error);
    }
});


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