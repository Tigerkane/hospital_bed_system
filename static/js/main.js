// static/js/main.js
// Auto-refresh availability for cards with data-hospital-id
async function refreshAvailability() {
  document.querySelectorAll('[data-hospital-id]').forEach(async (card) => {
    const id = card.dataset.hospitalId;
    try {
      const res = await fetch(`/api/hospital/${id}/availability`);
      if (!res.ok) return;
      const avail = await res.json();
      card.querySelectorAll('.icu-count').forEach(el => el.textContent = avail.icu);
      card.querySelectorAll('.oxygen-count').forEach(el => el.textContent = avail.oxygen);
      card.querySelectorAll('.normal-count').forEach(el => el.textContent = avail.normal);
      card.querySelectorAll('.vent-count').forEach(el => el.textContent = avail.ventilator);
    } catch (e) {
      console.error('refresh error', e);
    }
  });
}

let refreshInterval = null;
function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);
  refreshAvailability();
  refreshInterval = setInterval(refreshAvailability, 8000); // every 8s
}
window.addEventListener('load', startAutoRefresh);

// Simple toast messages
function showToast(msg, type='info') {
  const containerId = 'toast-container';
  let container = document.getElementById(containerId);
  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    Object.assign(container.style, {position:'fixed', right:'20px', bottom:'20px', zIndex:9999});
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.textContent = msg;
  t.className = 'app-toast ' + type;
  t.style.marginTop = '8px';
  container.appendChild(t);
  setTimeout(()=> t.classList.add('visible'), 20);
  setTimeout(()=> { t.classList.remove('visible'); setTimeout(()=> t.remove(),300); }, 4500);
}

// Confirm before booking (enhance booking form)
document.addEventListener('submit', function(e){
  const f = e.target;
  if (f && f.matches('.confirm-booking-form')) {
    // show confirm dialog
    if (!confirm('Confirm booking? Please check details.')) {
      e.preventDefault();
      showToast('Booking cancelled', 'warning');
    }
  }
});

// Optional: clickable copy for contact numbers
document.addEventListener('click', (e)=>{
  if (e.target && e.target.matches('.copy-contact')) {
    const text = e.target.dataset.contact;
    if (!text) return;
    navigator.clipboard?.writeText(text).then(()=> showToast('Contact copied', 'success'));
  }
});
