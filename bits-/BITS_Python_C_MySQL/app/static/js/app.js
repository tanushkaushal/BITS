function openModal(id){const el=document.getElementById(id);if(!el)return;el.classList.add('open');el.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';}
function closeModal(id){const el=document.getElementById(id);if(!el)return;el.classList.remove('open');el.setAttribute('aria-hidden','true');document.body.style.overflow='';}
function openComponentModal(){
  ['componentId','componentName','componentValue','componentLocation','componentNotes'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
  document.getElementById('componentQuantity').value='0';document.getElementById('componentCategory').value='';document.getElementById('componentModalTitle').textContent='Add component';openModal('componentModal');
}
function editComponent(item){
  document.getElementById('componentId').value=item.id;document.getElementById('componentName').value=item.name||'';document.getElementById('componentValue').value=item.component_value||'';document.getElementById('componentQuantity').value=item.quantity??0;document.getElementById('componentLocation').value=item.location||'';document.getElementById('componentNotes').value=item.notes||'';document.getElementById('componentCategory').value=item.category_id||'';document.getElementById('componentModalTitle').textContent='Edit component';openModal('componentModal');
}
function openCategoryModal(){openModal('categoryModal');}
document.addEventListener('click',e=>{if(e.target.classList.contains('modal-backdrop'))closeModal(e.target.id);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelectorAll('.modal-backdrop.open').forEach(el=>closeModal(el.id));}});
