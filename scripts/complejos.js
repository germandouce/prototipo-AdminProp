document.addEventListener('DOMContentLoaded', () => {
    const agregarBtn = document.getElementById('agregar-complejo-btn');
    const container = document.querySelector('.complejos-container');

    // Redirección al hacer click en un complejo
    function handleComplejoClick(e) {
        if (e.target.classList.contains('complejo-btn-funcional')) {
            const nombre = e.target.childNodes[0].textContent.trim();
            window.location.href = `unidades_funcionales.html?complejo=${encodeURIComponent(nombre)}`;
        }
    }
    container.addEventListener('click', handleComplejoClick);

    agregarBtn.addEventListener('click', () => {
        const nombre = prompt('Ingrese el nombre/dirección del complejo:');
        if (!nombre) return;
        const uf = prompt('Ingrese la cantidad de UF:');
        if (!uf || isNaN(uf)) return;

        const btn = document.createElement('button');
        btn.className = 'complejo-btn';
        btn.innerHTML = `${nombre} <span class="uf">${uf} UF</span>`;
        // Inserta antes del botón "Agregar complejo"
        container.insertBefore(btn, agregarBtn);
    });
});
