document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.unidades-container');

    function handleComplejoClick(e) {
        console.log("clicked");

        const row = e.target.closest('tr.funcional'); // busca el <tr> con clase funcional
        if (row) {
            console.log("funcional");

            // tomar el texto de la celda de la unidad
            const unidadCell = row.querySelector('td[data-label="Unidad"] .unit');
            const nombre = unidadCell ? unidadCell.textContent.trim() : "";

            // redirigir
            window.location.href = `vista_local.html?unidad=${encodeURIComponent(nombre)}`;
        }
    }

    container.addEventListener('click', handleComplejoClick);
});
