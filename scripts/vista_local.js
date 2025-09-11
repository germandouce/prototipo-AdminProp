function toggleTodos() {
    // Selecciona las celdas de la tabla
    const tabla = document.querySelector(".resumen-deuda table");
    const filas = tabla.querySelectorAll("tr");
    
    let celdaOcupado = filas[1].querySelector("td:nth-child(2)");
    let celdaPago = filas[2].querySelector("td:nth-child(2)");
    
    // Selecciona el nombre del cliente
    const nombreCliente = document.querySelector("h1[data-nombre]");
    const deudaTotal = document.querySelector("h1[data-deuda]");
    
    const mensaje = document.getElementById("mensaje-boton");
    mensaje.textContent = "Desocupada con éxito";
    mensaje.style.display = "block"; // mostrar


    // Mensaje debajo del botón
    // let mensaje = document.getElementById("mensaje-boton");
    if(!mensaje){
        mensaje = document.createElement("div");
        mensaje.id = "mensaje-boton";
        document.querySelector(".boton-desocupar").after(mensaje);
    }

    // Verifica si está ocupado o desocupado
    if(celdaOcupado.textContent.trim() === "Sí"){
        // Desocupar
        celdaOcupado.textContent = "No";
        celdaPago.textContent = "-";
        nombreCliente.textContent = "Desocupado";
        deudaTotal.textContent = "$000000";
        mensaje.textContent = "Unidad desocupada con éxito";
    } else {
        
        mensaje.textContent = "Esta unidad ya se encuentra desocupada";
    }

    setTimeout(() => {
        mensaje.style.display = "none";
    }, 3000); // 3 segundos

}
