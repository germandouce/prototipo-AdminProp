const selectMeses = document.getElementById('periodos');
const cuerpos = document.querySelectorAll('.periodo');

function actualizarTabla(mes) {
    const seleccionado = document.getElementById(mes);
    // mostrar la del mes seleccionado
    cuerpos.forEach(
        cuerpo => cuerpo.classList.add('hidden')
    );
    seleccionado.classList.remove('hidden')
}

// evento al cambiar
selectMeses.addEventListener('change', () => {
    actualizarTabla(selectMeses.value);
});

// mostrar la inicial
mostrarTabla(selectMeses.value);