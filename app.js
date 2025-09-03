document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-btn");
    const registerBtn = document.getElementById("register-btn");
    const loginScreen = document.getElementById("login-screen");
    const appContainer = document.getElementById("app");
    const links = document.querySelectorAll(".sidebar nav a");
    const pages = document.querySelectorAll(".page");

    if (loginBtn) {
        loginBtn.addEventListener("click", () => {
            loginScreen.classList.remove("active");
            appContainer.classList.remove("hidden");

            // Forzar que la vista activa sea "inicio"
            pages.forEach(page => page.classList.remove("active"));
            document.getElementById("inicio").classList.add("active");

            links.forEach(l => l.classList.remove("active"));
            document.querySelector('[data-page="inicio"]').classList.add("active");
        });
    }

    if (registerBtn) {
        registerBtn.addEventListener("click", () => {
            alert("Funcionalidad de registro no implementada en este prototipo.");
        });
    }

    links.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            links.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
            pages.forEach(page => page.classList.remove("active"));
            const pageId = link.dataset.page;
            document.getElementById(pageId).classList.add("active");
        });
    });
});