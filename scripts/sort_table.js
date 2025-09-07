document.addEventListener("DOMContentLoaded", () => {
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
})