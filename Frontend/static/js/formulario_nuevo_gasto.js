// Mostrar el nombre/dirección del complejo en el encabezado
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const complejo = params.get('complejo');
    if (complejo) {
        document.getElementById('direccion-complejo').textContent = complejo;
    }
});
// Mostrar formulario modal al hacer click en "Agregar gasto"
document.getElementById('add-expense-unit-btn').addEventListener('click', function() {
    document.getElementById('gasto-modal-overlay').style.display = 'flex';
});
document.getElementById('gasto-cancel-btn').addEventListener('click', function() {
    document.getElementById('gasto-form').reset();
    document.getElementById('gasto-modal-overlay').style.display = 'none';
});
document.getElementById('gasto-form').addEventListener('submit', function(e) {
    e.preventDefault();
    // Solo agrega a la tabla de septiembre
    const fecha = document.getElementById('fecha-gasto').value;
    const detalle = document.getElementById('detalle-gasto').value;
    const monto = document.getElementById('monto-gasto').value;
    const tbody = document.getElementById('septiembre-2025');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td data-label="Fecha">${fecha}</td>
        <td data-label="Detalle" class="tenant">${detalle}</td>
        <td data-label="Monto" class="rent">$${monto}</td>
    `;
    tbody.appendChild(tr);
    document.getElementById('gasto-form').reset();
    document.getElementById('gasto-modal-overlay').style.display = 'none';
});