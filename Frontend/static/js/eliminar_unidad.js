document.addEventListener('DOMContentLoaded', function() {
    const btnEliminar = document.getElementById('btnEliminar');
    if (btnEliminar) {
        btnEliminar.addEventListener('click', function () {
            Swal.fire({
                title: "¿Seguro que quiere eliminar la unidad?",
                text: "Se borrará todo lo relacionado con la unidad. Esta acción no se puede deshacer.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Confirmar",
                cancelButtonText: "Cancelar"
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const consortiumId = btnEliminar.getAttribute('data-consortium-id');
                    const unitId = btnEliminar.getAttribute('data-unit-id');
                    try {
                        const response = await fetch(
                            `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/eliminar`,
                            {method: 'DELETE'}
                        );
                        if (response.ok) {
                            Swal.fire({
                                title: "Eliminado",
                                text: "La unidad ha sido eliminada.",
                                icon: "success"
                            }).then(() => {
                                location.assign(`/consorcios/${consortiumId}/unidades_funcionales`);
                            });
                        } else {
                            Swal.fire({
                                title: "Error",
                                text: "No se ha podido eliminar la unidad.",
                                icon: "error"
                            });
                        }
                    } catch (e) {
                        Swal.fire({
                            title: "Error de red",
                            text: "",
                            icon: "error"
                        });
                    }
                }
            });
        });
    }
});