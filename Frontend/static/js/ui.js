// scripts/ui.js
function showToast(msg, ms=2000){
    const t=document.createElement('div');
    t.className='toast'; t.textContent=msg;
    document.body.appendChild(t);
    setTimeout(()=>t.remove(), ms);
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
window.UI={showToast,openModal};
