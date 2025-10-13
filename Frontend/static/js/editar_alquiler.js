document.addEventListener('DOMContentLoaded', function() {
    function agregarListenerEditarAlquiler() {
        const btnEditarAlquiler = document.getElementById('btnEditarAlquiler');
        if (btnEditarAlquiler) {
            btnEditarAlquiler.addEventListener('click', async function () {
                const consortiumId = btnEditarAlquiler.getAttribute('data-consortium-id');
                const unitId = btnEditarAlquiler.getAttribute('data-unit-id');
                const contenedorPrecio = document.getElementById('tdAlquiler');
                const contenidoActual = contenedorPrecio.innerHTML;

                contenedorPrecio.innerHTML = `<input type="number" id="inputAlquiler" class="form-control" min="0" step="0.01" required>
                                              <button id="btnGuardarAlquiler" class="btn btn-primary btn-sm">Guardar</button>
                                              <button id="btnCancelarEdicionAlquiler">Cancelar</button>`;
                const btnGuardarAlquiler = document.getElementById('btnGuardarAlquiler');
                const btnCancelarEdicionAlquiler = document.getElementById('btnCancelarEdicionAlquiler');

                btnGuardarAlquiler.addEventListener('click', async function () {
                    const rent_value = document.getElementById('inputAlquiler').value;
                    try {
                        const response = await fetch(
                            `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/editar_alquiler`,
                            {
                                method: 'PATCH',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ rent_value })
                            }
                        );
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('Error al establecer precio del alquiler');
                        }
                    } catch (e) {
                        alert('Error de red');
                    }
                });

                btnCancelarEdicionAlquiler.addEventListener('click', function () {
                    contenedorPrecio.innerHTML = contenidoActual;
                    agregarListenerEditarAlquiler(); // Volver a asociar el listener
                });
            });
        }
    }
    agregarListenerEditarAlquiler();
});
