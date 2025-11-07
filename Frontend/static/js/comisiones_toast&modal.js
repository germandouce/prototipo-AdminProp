function showToast(msg, ms=2000){
    const t=document.createElement('div'); t.className='toast'; t.textContent=msg;
    document.body.appendChild(t); setTimeout(()=>t.remove(), ms);
}
function openModal({title, bodyHTML, onConfirm}){
    const bd=document.createElement('div'); bd.className='backdrop';
    const m=document.createElement('div'); m.className='modal';
    m.innerHTML=`
      <header><h3>${title}</h3><button id="mClose" class="btn-secondary">✕</button></header>
      <div class="modal-body">${bodyHTML}</div>
      <footer>
        <button id="mCancel" class="btn-secondary">Cancelar</button>
        <button id="mOk" class="btn-primary">Confirmar exportación</button>
      </footer>`;
    function close(){ bd.remove(); m.remove(); }
    bd.addEventListener('click', close);
    m.querySelector('#mClose').addEventListener('click', close);
    m.querySelector('#mCancel').addEventListener('click', close);
    m.querySelector('#mOk').addEventListener('click', ()=>{ onConfirm&&onConfirm(); close(); });
    document.body.append(bd,m);
}

const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const num = t => parseInt(String(t).replace(/[^\d\-]/g,''))||0;

function leerTabla(){
    let total=0, incl=0, sumPct=0;
    $$('#tbl tbody tr').forEach(tr=>{
        const est = (tr.cells[5]?.textContent||'').trim();
        if(est.startsWith('Incl')){
            total += num(tr.cells[4].textContent);
            incl++;
            sumPct += num(tr.cells[3].textContent);
        }
    });
    return { total, incl, pct: incl? (sumPct/incl): 0 };
}

function refrescarKPI(){
    const {total, incl, pct} = leerTabla();
    $('#kpiTotal').textContent = '$' + total.toLocaleString('es-AR');
    $('#kpiUnits').textContent = String(incl);
    $('#kpiPct').textContent = pct.toFixed(1) + '%';
}

// CALCULAR
// $('#btnCalcular').addEventListener('click', ()=>{
//     // feedback de avance
//     const periodo = $('#selPeriodo').value, amb = $('#selAmbito').value;
//     $('#status').textContent = `Cálculo listo para ${periodo} · ${amb}`;
//     $('#status').classList.add('active');

//     // mostrar KPIs, habilitar acciones
//     $('#kpiWrap').style.display='grid';
//     $('#btnAplicar').disabled=false;
//     $('#btnExportar').disabled=false;

//     // recalcular KPIs (usando la tabla actual como demo)
//     refrescarKPI();
//     showToast('Comisiones calculadas');
// });

$('#btnCalcular').addEventListener('click', ()=>{
    const periodo = $('#selPeriodo').value;
    const consorcioId = $('#selAmbito').value;

    window.location.href = `/comisiones?periodo=${periodo}&consorcio_id=${consorcioId}`;
});


document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const formDiv = document.getElementById("formularioParametros");

  if (formDiv && params.toString()) {
    formDiv.style.display = "block";
  }

  const form = document.getElementById("formParametros");
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const valor = document.getElementById("valorInput").value;
      const select = document.getElementById("selAmbito");
      const consortiumId = select ? select.value : null;

      if (!consortiumId) {
        Swal.fire({
          title: "Error",
          text: "Debe seleccionar un consorcio antes de actualizar.",
          icon: "error"
        });
        return;
      }

      const parsedValor = parseFloat(valor);
      if (isNaN(parsedValor)) {
        Swal.fire({
          title: "Valor inválido",
          text: "Ingrese un valor numérico válido para la comisión.",
          icon: "warning"
        });
        return;
      }

      Swal.fire({
        title: "¿Desea actualizar la comisión?",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Sí, actualizar",
        cancelButtonText: "Cancelar"
      }).then(async (result) => {
        if (result.isConfirmed) {
          try {
            const response = await fetch(`/consortiums/${consortiumId}`, {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({ admin_commission: parsedValor })
            });

            if (response.ok) {
              Swal.fire({
                title: "Comisión actualizada",
                icon: "success"
              }).then(() => { 
                window.location.href = "/comisiones";
              });
            } else {
              let errorData;
              try {
                errorData = await response.json();
              } catch {
                errorData = { error: await response.text() };
              }

              Swal.fire({
                title: "Error",
                text: errorData.error || "No se pudo actualizar la comisión.",
                icon: "error"
              });
            }
          } catch (err) {
            console.error("Error en la solicitud PATCH:", err);
            Swal.fire({
              title: "Error de red",
              text: "No se pudo conectar con el servidor.",
              icon: "error"
            });
          }
        }
      });
    });
  }
});


// APLICAR A RENDICIÓN
$('#btnAplicar').addEventListener('click', ()=>{
    showToast('Comisión aplicada a la rendición de ' + $('#selPeriodo').value, 2500);
});

// EXPORTAR (vista previa)
$('#btnExportar').addEventListener('click', ()=>{
    const bodyHTML = `
      <p><b>Período:</b> ${$('#selPeriodo').value}<br>
         <b>Ámbito:</b> ${$('#selAmbito').value}</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
        <div><b>Total comisión</b><br>${$('#kpiTotal').textContent}</div>
        <div><b>Unidades incluidas</b><br>${$('#kpiUnits').textContent}</div>
        <div><b>Promedio %</b><br>${$('#kpiPct').textContent}</div>
      </div>
      <hr>
      ${$('#detTabla').open ? document.querySelector('#detTabla table').outerHTML : ''}
    `;
    openModal({
        title: 'Vista previa de exportación',
        bodyHTML,
        onConfirm: ()=>{
            const fn = `comisiones_${$('#selPeriodo').value.replace('/','-')}.pdf`;
            showToast('Exportado: ' + fn, 2500);
        }
    });
});

// si cambian % o base, simulamos “pendiente de recálculo”
$('#inpPct, input[name="base"], #chkExcl').forEach
    ? $('#inpPct, input[name="base"], #chkExcl') // fallback muy básico
    : null;