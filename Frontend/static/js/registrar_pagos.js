document.addEventListener('DOMContentLoaded', () => {
    const btnFormularioPagos = document.getElementById('btnFormularioPagos');
    const modalOverlay = document.getElementById('modal-overlay');
    const btnCancelarRegistroPago = document.getElementById('btnCancelarRegistroPago')
    const btnRegistrarPagos = document.getElementById('btnRegistrarPagos');
    const tablaPagosBody = document.querySelector('#tabla-pagos tbody');

    const consortiumId = btnFormularioPagos.getAttribute('data-consortium-id') || document.querySelector('[data-consortium-id]').getAttribute('data-consortium-id');
    const unitId = btnFormularioPagos.getAttribute('data-unit-id') || document.querySelector('[data-unit-id]').getAttribute('data-unit-id');
    const tenant = btnFormularioPagos.getAttribute('data-tenant')

    btnFormularioPagos.addEventListener('click', async () => {
        modalOverlay.style.display = 'flex';
        const response = await fetch(`/pagos/${consortiumId}/${unitId}/${tenant}`);
        const pagos = await response.json();
        console.log(pagos)

        tablaPagosBody.innerHTML = '';

        if (Array.isArray(pagos)) {
            pagos.forEach(pago => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${pago.date}</td>
                    <td>FALTA DESCRIPCIÓN</td>
                    <td>${pago.amount}</td>
                    <td><input type="checkbox" class="pago-checkbox" data-payment-id="${pago.id}"></td>
                `;
                tablaPagosBody.appendChild(row);
            });
        } else if (pagos.error) {
        tablaPagosBody.innerHTML = `<tr><td colspan="4">${pagos.error}</td></tr>`;
    }
    });

    btnCancelarRegistroPago.addEventListener('click', () => {
        modalOverlay.style.display = 'none';
    })
})