
async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch("/token", {
        method: "POST",
        body: formData
    });
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        showApp();
    } else {
        alert("Login failed");
    }
}

async function register(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch("/users/", {
        method: "POST",
        body: formData
    });
    if (response.ok) {
        alert("Registration successful! Please log in.");
        // Можна автоматично логінити користувача тут
    } else {
        alert("Registration failed");
    }
}

function logout() {
    localStorage.removeItem("access_token");
    showAuth();
}
