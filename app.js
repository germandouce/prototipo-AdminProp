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

    function sortTableByColumnDesc(tableSelector, columnIndex) {
        const table = document.querySelector(tableSelector);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            // Extrae el valor numérico (elimina $ y .)
            const getValue = tr => {
                const text = tr.children[columnIndex].textContent.replace(/[$. ]/g, '').replace(',', '');
                return parseInt(text, 10) || 0;
            };
            return getValue(b) - getValue(a);
        });

        // Limpia y re-agrega las filas ordenadas
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }

    // Alquiler: columna 2
    document.getElementById('sort-alquiler-desc').addEventListener('click', () => {
        sortTableByColumnDesc('#clientes table', 2);
    });
    // Ordinarias: columna 3
    document.getElementById('sort-ordinarias-desc').addEventListener('click', () => {
        sortTableByColumnDesc('#clientes table', 3);
    });
    // Extraordinarias: columna 4
    document.getElementById('sort-extraordinarias-desc').addEventListener('click', () => {
        sortTableByColumnDesc('#clientes table', 4);
    });
    // Deuda: columna 5
    document.getElementById('sort-deuda-desc').addEventListener('click', () => {
        sortTableByColumnDesc('#clientes table', 5);
    });
    // Pago: columna 6
    document.getElementById('sort-pago-desc').addEventListener('click', () => {
        sortTableByColumnDesc('#clientes table', 6);
    });
});