document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.unidades-container');
    const addBtn = document.getElementById('add-unit-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const form = document.getElementById('unit-form');
    const cancelBtn = document.getElementById('cancel-btn');

    // Mostrar modal
    addBtn.addEventListener('click', () => {
        modalOverlay.style.display = 'flex';
    });

    // Cerrar modal con cancelar
    cancelBtn.addEventListener('click', () => {
        form.reset();
        modalOverlay.style.display = 'none';
    });

    // Guardar nueva unidad
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const unidad = form.unidad.value.trim();
        const inquilino = form.inquilino.value.trim();
        const alquiler = form.alquiler.value.trim();

        // Calcular número avatar
        const avatars = container.querySelectorAll('.avatar');
        let nextNumber = 1;
        if (avatars.length > 0) {
            const lastNum = parseInt(avatars[avatars.length - 1].textContent.trim(), 10);
            nextNumber = lastNum + 1;
        }
        const formattedNumber = String(nextNumber).padStart(3, '0');

        // Crear fila
        const tr = document.createElement('tr');
        tr.classList.add('funcional');
        tr.innerHTML = `
      <td data-label="Unidad">
        <span class="unit"><span class="avatar">${formattedNumber}</span> ${unidad}</span>
      </td>
      <td data-label="Inquilino" class="tenant">${inquilino}</td>
      <td data-label="Alquiler" class="rent">${alquiler}</td>
      <td data-label="Estado de pago"><span class="status pending" aria-label="Pendiente">● Pendiente</span></td>
    `;

        container.appendChild(tr);

        // Resetear y cerrar modal
        form.reset();
        modalOverlay.style.display = 'none';
    });
});
