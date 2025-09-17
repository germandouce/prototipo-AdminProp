// =======================
// 1) TU FUNCIÓN (ajustada mínimamente)
// =======================
function toggleTodos() {
  // Selecciona las celdas de la tabla
  const tabla = document.querySelector(".resumen-deuda table");
  const filas = tabla.querySelectorAll("tr");

  let celdaOcupado = filas[1].querySelector("td:nth-child(2)");
  let celdaPago = filas[2].querySelector("td:nth-child(2)");

  // Selecciona el nombre del cliente y la deuda
  const nombreCliente = document.querySelector("h1[data-nombre]");
  const deudaTotal = document.querySelector("h1[data-deuda]");

  // Mensaje debajo del botón (crearlo si no existe)
  let mensaje = document.getElementById("mensaje-boton");
  if (!mensaje) {
    mensaje = document.createElement("div");
    mensaje.id = "mensaje-boton";
    document.querySelector(".boton-desocupar").after(mensaje);
  }

  // Verifica si está ocupado o desocupado
  if (celdaOcupado.textContent.trim() === "Sí") {
    // Desocupar
    celdaOcupado.textContent = "No";
    celdaPago.textContent = "-";
    nombreCliente.textContent = "Desocupado";
    deudaTotal.textContent = "$000000";
    mensaje.textContent = "Unidad desocupada con éxito";
  } else {
    mensaje.textContent = "Esta unidad ya se encuentra desocupada";
  }

  // Mostrar y ocultar el mensaje
  mensaje.style.display = "block";
  setTimeout(() => { mensaje.style.display = "none"; }, 3000);
}

// =======================
// 2) MODAL CAMBIAR INQUILINO (nuevo)
// =======================
const $ = (s) => document.querySelector(s);

const modal = $("#modalInq");
const backdrop = $("#backdrop");
const btnOpen = $("#btnCambiarInq");
const btnClose = $("#btnCerrar");
const btnCancel = $("#btnCancelar");
const btnSave = $("#btnGuardar");

function openModal() {
  backdrop.style.display = "block";
  modal.style.display = "block";
  // Prefill con valores actuales (si hay)
  $("#inpNombre").value = ($("h1[data-nombre]")?.textContent || "").trim().toLowerCase() === "desocupado" ? "" : $("h1[data-nombre]").textContent.trim();
  const alquilerTxt = $("#tdAlquiler").textContent.replace(/[^\d]/g, "");
  $("#inpAlquiler").value = alquilerTxt || "";
  $("#inpFinContrato").value = $("#tdFinContrato").dataset?.iso || "";
  $("#inpNombre").focus();
}

function closeModal() {
  backdrop.style.display = "none";
  modal.style.display = "none";
}

// Abrir/cerrar
btnOpen.addEventListener("click", openModal);
btnClose.addEventListener("click", closeModal);
btnCancel.addEventListener("click", closeModal);
backdrop.addEventListener("click", closeModal);
window.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

// Guardar cambios del modal
btnSave.addEventListener("click", () => {
  const nombre = $("#inpNombre").value.trim();
  const alquiler = parseInt($("#inpAlquiler").value, 10);
  const fin = $("#inpFinContrato").value; // yyyy-mm-dd

  // Validaciones mínimas
  let mensaje = document.getElementById("mensaje-boton");
  if (!mensaje) {
    mensaje = document.createElement("div");
    mensaje.id = "mensaje-boton";
    document.querySelector(".boton-desocupar").after(mensaje);
  }

  if (!nombre) {
    mensaje.textContent = "Ingresá el nombre del inquilino";
    mensaje.style.display = "block";
    setTimeout(() => (mensaje.style.display = "none"), 3000);
    $("#inpNombre").focus();
    return;
  }
  if (!Number.isFinite(alquiler) || alquiler <= 0) {
    mensaje.textContent = "Ingresá un valor de alquiler válido";
    mensaje.style.display = "block";
    setTimeout(() => (mensaje.style.display = "none"), 3000);
    $("#inpAlquiler").focus();
    return;
  }
  if (!fin) {
    mensaje.textContent = "Seleccioná la fecha de fin de contrato";
    mensaje.style.display = "block";
    setTimeout(() => (mensaje.style.display = "none"), 3000);
    $("#inpFinContrato").focus();
    return;
  }

  // Actualiza UI principal
  $("h1[data-nombre]").textContent = nombre;
  $("#tdOcupado").textContent = "Sí";

  $("#tdAlquiler").textContent = new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0
  }).format(alquiler);

  const fecha = new Date(fin);
  const legible = fecha.toLocaleDateString("es-AR", {
    year: "numeric", month: "long", day: "2-digit"
  });
  $("#tdFinContrato").textContent = legible;
  $("#tdFinContrato").dataset.iso = fin;

  // Feedback
  let deuda = document.querySelector("h1[data-deuda]");
  if (deuda) deuda.textContent = "$00000"; // no tocamos lógica de deuda, solo ejemplo

  mensaje.textContent = "Inquilino actualizado con éxito";
  mensaje.style.display = "block";
  setTimeout(() => (mensaje.style.display = "none"), 3000);

  closeModal();
});
