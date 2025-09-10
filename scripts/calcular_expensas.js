document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('calcular-expensas-septiembre');
    if (!btn) return;

    btn.addEventListener('click', () => {
        // Sumar los montos de la tabla de septiembre
        const gastosTable = document.getElementById('septiembre-2025');
        if (!gastosTable) {
            console.warn('No se encontró la tabla de gastos de septiembre');
            return;
        }
        let total = 0;
        Array.from(gastosTable.rows).forEach(row => {
            // Tercera columna = monto
            const montoCell = row.cells[2];
            if (montoCell) {
                const monto = montoCell.textContent.replace(/[$. ]/g, '').replace(',', '');
                total += parseInt(monto, 10) || 0;
            }
        });

        // Selecciona solo las filas de la tabla de unidades funcionales (usando el id)
        const unidadesTable = document.getElementById('tabla-unidades-septiembre');
        if (!unidadesTable) {
            console.warn('No se encontró la tabla de unidades funcionales');
            return;
        }
        const unidadesRows = Array.from(unidadesTable.rows);
        const cantidadUnidades = unidadesRows.length;
        const valorPorUnidad = cantidadUnidades > 0 ? Math.round(total / cantidadUnidades) : 0;

        unidadesRows.forEach(tr => {
            // Quinta columna = expensas septiembre
            const expensaCell = tr.cells[4];
            if (expensaCell) {
                expensaCell.textContent = valorPorUnidad > 0 ? `$${valorPorUnidad.toLocaleString('es-AR')}` : '';
            }
        });

        btn.textContent = `Expensas septiembre calculadas: $${valorPorUnidad.toLocaleString('es-AR')}`;
        btn.disabled = true;
    });
});