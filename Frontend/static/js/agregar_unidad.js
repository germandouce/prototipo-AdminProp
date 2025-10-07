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
});
