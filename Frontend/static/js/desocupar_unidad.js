document.addEventListener('DOMContentLoaded', function() {
    const btnDesocupar = document.getElementById('btnDesocupar');
    const formOcupar = document.getElementById('formOcupar');
    const clienteDiv = document.querySelector('.info-local [data-nombre]').parentElement;

    function renderFormOcupar(consortiumId, unitId) {
        clienteDiv.innerHTML = `
            <h1 data-nombre></h1>
            <form id="formOcupar" data-consortium-id="${consortiumId}" data-unit-id="${unitId}">
                <input type="text" id="inputInquilino" name="ocupar" placeholder="Nombre de nuevo inquilino">
                <button type="submit" class="btn btn-primary">Establecer</button>
            </form>
        `;
        agregarListenerFormOcupar();
    }

    function renderInquilino(nombre, consortiumId, unitId) {
        clienteDiv.innerHTML = `
            <h1 data-nombre>${nombre}</h1>
            <button type="button" id="btnDesocupar" class="btn btn-secondary" data-consortium-id="${consortiumId}" data-unit-id="${unitId}">
                Desocupar
            </button>
        `;
        agregarListenerBtnDesocupar();
    }

    function agregarListenerBtnDesocupar() {
        const btn = document.getElementById('btnDesocupar');
        if (btn) {
            btn.addEventListener('click', async function() {
                Swal.fire({
                    title: "¿Seguro que quiere desocupar la unidad?",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonText: "Sí",
                    cancelButtonText: "Cancelar"
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        const consortiumId = btn.getAttribute('data-consortium-id');
                        const unitId = btn.getAttribute('data-unit-id');
                        try {
                            const response = await fetch(
                                `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/desocupar`,
                                { method: 'PATCH' }
                            );
                            if (response.ok) {
                                Swal.fire({
                                    title: "Unidad desocupada",
                                    icon: "success"
                                });
                                renderFormOcupar(consortiumId, unitId);
                            } else {
                                Swal.fire({
                                    title: "Error",
                                    text: "Error al desocupar la unidad",
                                    icon: "error"
                                });
                            }
                        } catch (e) {
                            Swal.fire({
                                title: "Error de red",
                                icon: "error"
                            });
                        }
                    }
                });
            });
        }
    }

    function agregarListenerFormOcupar() {
        const form = document.getElementById('formOcupar');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const consortiumId = form.getAttribute('data-consortium-id');
                const unitId = form.getAttribute('data-unit-id');
                const tenant = document.getElementById('inputInquilino').value;
                try {
                    const response = await fetch(
                        `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/ocupar`,
                        {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ tenant })
                        }
                    );
                    if (response.ok) {
                        Swal.fire({
                            title: "Unidad ocupada",
                            icon: "success"
                        });
                        renderInquilino(tenant, consortiumId, unitId);
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: "Error al establecer inquilino",
                            icon: "error"
                        });
                    }
                } catch (e) {
                    Swal.fire({
                        title: "Error de red",
                        icon: "error"
                    });
                }
            });
        }
    }

    agregarListenerBtnDesocupar();
    agregarListenerFormOcupar();
});
