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
        const response = await fetch(`/pagos/${consortiumId}/${unitId}/${tenant}`);
        const pagos = await response.json();
        modalOverlay.style.display = 'flex';

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

    btnRegistrarPagos.addEventListener('click', async () => {
        const checkboxes = document.querySelectorAll('.pago-checkbox:checked');
        const cantidad = checkboxes.length;
        if (cantidad < 1) {
            Swal.fire({
                title: "Error",
                text: "Selecciona al menos un pago.",
                icon: "error"
            });
        } else {
            Swal.fire({
                title: "¿Seguro?",
                text: `Estás a punto de registrar ${cantidad} pagos`,
                icon: "question",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Si"
            }).then(async (result) => {
                if (result.isConfirmed) {
                    let huboError = false;
                    for (const checkbox of checkboxes) {
                        const paymentId = checkbox.getAttribute('data-payment-id');
                        const response = await fetch(`/registrar_pago/${paymentId}`, {method: 'DELETE'});
                        if (!response.ok) {
                            huboError = true;
                            break;
                        }
                    }
                    if (huboError) {
                        Swal.fire({
                            title: "Error",
                            text: "Ocurrió un error al registrar los pagos.",
                            icon: "error"
                        });
                    } else {
                        modalOverlay.style.display = 'none';
                        Swal.fire({
                            title: "Hecho",
                            text: "Los pagos se han registrado.",
                            icon: "success"
                        });
                    }
                }
            });
        }
    });

    btnCancelarRegistroPago.addEventListener('click', () => {
        modalOverlay.style.display = 'none';
    })
})