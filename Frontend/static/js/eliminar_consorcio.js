document.addEventListener('DOMContentLoaded', function() {
    const btnEliminar = document.getElementById('btnEliminarConsorcio');
    if (btnEliminar) {
        btnEliminar.addEventListener('click', function () {
            Swal.fire({
                title: "¿Seguro que quiere eliminar el consorcio?",
                text: "Se borrará todo lo relacionado con la unidad, incluidas unidades funcionales, pagos, expensas, etc. Esta acción no se puede deshacer.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Confirmar",
                cancelButtonText: "Cancelar"
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const consortiumId = btnEliminar.getAttribute('data-consortium-id');
                    try {
                        const response = await fetch(
                            `/consorcios/${consortiumId}/eliminar`,
                            {method: 'DELETE'}
                        );
                        if (response.ok) {
                            Swal.fire({
                                title: "Eliminado",
                                text: "El consorcio ha sido eliminado.",
                                icon: "success"
                            }).then(() => {
                                location.assign(`/consorcios`);
                            });
                        } else {
                            Swal.fire({
                                title: "Error",
                                text: "No se ha podido eliminar el consorcio.",
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