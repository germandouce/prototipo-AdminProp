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
$('#btnCalcular').addEventListener('click', ()=>{
    // feedback de avance
    const periodo = $('#selPeriodo').value, amb = $('#selAmbito').value;
    $('#status').textContent = `Cálculo listo para ${periodo} · ${amb}`;
    $('#status').classList.add('active');

    // mostrar KPIs, habilitar acciones
    $('#kpiWrap').style.display='grid';
    $('#btnAplicar').disabled=false;
    $('#btnExportar').disabled=false;

    // recalcular KPIs (usando la tabla actual como demo)
    refrescarKPI();
    showToast('Comisiones calculadas');
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