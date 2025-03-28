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

        window.isSuperAdmin = data.is_superadmin;

        if (data.is_superadmin) {
            const userListItemEl = document.getElementById("user-list-item");
            const pendingApprovalItemEl = document.getElementById("pending-approval-item");
            const adminOrdersBtnEl = document.getElementById("adminOrdersBtn");

            if (userListItemEl) {
                userListItemEl.style.display = "block";
            }
            if (pendingApprovalItemEl) {
                pendingApprovalItemEl.style.display = "block";
            }
            if (adminOrdersBtnEl) {
                adminOrdersBtnEl.style.display = "inline-block";
            }

            // Показать кнопки чат-админа
            const createChatBtn = document.getElementById("create-chat-btn");
            if (createChatBtn) {
                createChatBtn.style.display = "block";
            }

            // Если есть другие элементы (например, "add participants" кнопка), тоже показать
            const addBtns = document.querySelectorAll(".btn-add-participants");
            addBtns.forEach(btn => {
                btn.style.display = "block";
            });

        }
    } catch (error) {
        console.error("Error checking super admin status:", error);
    }
});
