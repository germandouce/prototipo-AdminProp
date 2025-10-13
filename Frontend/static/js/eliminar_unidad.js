document.addEventListener('DOMContentLoaded', function() {
    const btnEliminar = document.getElementById('btnEliminar');
    if (btnEliminar) {
        btnEliminar.addEventListener('click', async function () {
            if (confirm('¿Seguro que quiere eliminar la unidad? No podrá deshacer esta acción.')) {
                const consortiumId = btnEliminar.getAttribute('data-consortium-id');
                const unitId = btnEliminar.getAttribute('data-unit-id');
                try {
                    const response = await fetch(
                        `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/eliminar`,
                        {method: 'DELETE'}
                    );
                    if (response.ok) {
                        location.assign(`/consorcios/${consortiumId}/unidades_funcionales`);
                    } else {
                        alert('Error al eliminar la unidad');
                    }
                } catch (e) {
                    alert('Error de red');
                }
            }
        });
    }
})