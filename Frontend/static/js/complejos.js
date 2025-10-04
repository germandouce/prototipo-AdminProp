document.addEventListener('DOMContentLoaded', () => {
    const agregarBtn = document.getElementById('agregar-complejo-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const form = document.getElementById('block-form');

    agregarBtn.addEventListener('click', () => {
        modalOverlay.style.display = 'flex';
    });

    cancelBtn.addEventListener('click', () => {
        form.reset();
        modalOverlay.style.display = 'none';
    });
});
