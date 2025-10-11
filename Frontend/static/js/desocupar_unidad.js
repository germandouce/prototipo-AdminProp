document.addEventListener('DOMContentLoaded', function() {
    const btnDesocupar = document.getElementById('btnDesocupar');
    const formOcupar = document.getElementById('formOcupar');
    if (btnDesocupar) {
        btnDesocupar.addEventListener('click', async function() {
            if (confirm('¿Seguro que quiere desocupar la unidad?')) {
                const consortiumId = btnDesocupar.getAttribute('data-consortium-id');
                const unitId = btnDesocupar.getAttribute('data-unit-id');
                try {
                    const response = await fetch(
                        `/consorcios/${consortiumId}/unidades_funcionales/${unitId}/desocupar`,
                        { method: 'PATCH' }
                    );
                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Error al desocupar la unidad');
                    }
                } catch (e) {
                    alert('Error de red');
                }
            }
        });
    }

    if (formOcupar) {
        formOcupar.addEventListener('submit', async function(e) {
            e.preventDefault();
            const consortiumId = formOcupar.getAttribute('data-consortium-id');
            const unitId = formOcupar.getAttribute('data-unit-id');
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
                    location.reload();
                } else {
                    alert('Error al establecer inquilino');
                }
            } catch (e) {
                alert('Error de red');
            }
        });
    }
});