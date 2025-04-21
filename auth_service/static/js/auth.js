// auth.js
async function getTokenFromDatabase() {
    const userId = localStorage.getItem("user_id");
    const response = await fetch(`/get-user-token/${userId}`, {
        headers: { "Content-Type": "application/json" }
    });

    if (!response.ok) {
        console.log("Don't have access token. Redirecting to login page.");
        window.location.href = '/login';
        return null;
    }

    const data = await response.json();
    const token = data.access_token;

    const isValid = await verifyTokenOnServer(token);
    if (!isValid) {
        const newToken = await getNewAccessToken();
        if (!newToken) {
            window.location.href = '/login';
            return null;
        }
        return newToken;
    }


    return token;
}

async function verifyTokenOnServer(token) {
    const response = await fetch(`/verify-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token })
    });

    const data = await response.json();
    return data.valid;
}


async function getNewAccessToken() {
    const refreshToken = getCookie('refresh_token');
    if (!refreshToken) {
        console.log("Refresh token not found. Redirecting to login page.");
        return null;
    }

    const response = await fetch('/refresh-token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
    });

    const data = await response.json();
    if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        return data.access_token;
    } else {
        console.log("Didn't get new access token. Redirecting to login page.");
        return null;
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}