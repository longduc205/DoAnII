/**
 * Sentinel Scanner, frontend behavior.
 * Scoped, dependency-free. Only wires up what server-rendered HTML needs.
 */

document.addEventListener('DOMContentLoaded', () => {
  initScanForm();
  initToasts();
  initHistoryTable();
  initFindingExpand();
  exposeDeleteScan();
});

/* -------------------------------------------------------------------------
   Scan form: show inline progress, then let the form submit normally so
   Flask can run the scan and redirect to /results.
   -------------------------------------------------------------------------*/
function initScanForm() {
  const form = document.getElementById('scan-form');
  if (!form) return;

  const progress = document.getElementById('scan-progress');
  const progressFill = document.getElementById('scan-progress-fill');
  const progressTarget = document.getElementById('scan-progress-target');
  const submitBtn = document.getElementById('btn-launch-scan');
  const stepEls = Array.from(document.querySelectorAll('#scan-steps .step'));

  form.addEventListener('submit', () => {
    // Don't preventDefault; we want the browser to actually POST and let
    // Flask's synchronous scanner run, then 302 to results.
    if (progress) {
      progress.hidden = false;
      progress.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    if (progressTarget) {
      const url = form.elements['target_url']?.value || '';
      progressTarget.textContent = 'Target: ' + url;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-disabled', 'true');
    }

    animateSteps(stepEls, progressFill);
  });
}

/* Animate steps as a *visual estimate* while the synchronous scan runs. */
function animateSteps(stepEls, progressFill) {
  if (!stepEls.length) return;

  let idx = 0;
  const total = stepEls.length;

  function tick() {
    if (idx > 0) stepEls[idx - 1].classList.replace('step--active', 'step--done');
    if (idx < total) {
      stepEls[idx].classList.add('step--active');
      const pct = ((idx + 0.7) / total) * 100;
      if (progressFill) progressFill.style.width = pct + '%';
      idx++;
      // Steps don't all take the same time; bias toward crawl + SQLi.
      const delays = [1100, 1800, 1400, 900];
      setTimeout(tick, delays[Math.min(idx - 1, delays.length - 1)]);
    } else {
      // Hold near 100% until the server response arrives (page navigates away).
      if (progressFill) progressFill.style.width = '95%';
    }
  }
  tick();
}

/* -------------------------------------------------------------------------
   Toasts, server-rendered. Wire up close button + auto-dismiss.
   -------------------------------------------------------------------------*/
function initToasts() {
  const toasts = document.querySelectorAll('.toast');
  if (!toasts.length) return;

  toasts.forEach((toast) => {
    if (window.lucide) lucide.createIcons({ nodes: [toast] });

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismissToast(toast));

    const delay = parseInt(toast.dataset.autoDismiss, 10) || 5000;
    setTimeout(() => dismissToast(toast), delay);
  });
}

function dismissToast(toast) {
  if (!toast || toast.dataset.dismissing === '1') return;
  toast.dataset.dismissing = '1';
  toast.style.transition = 'opacity 200ms, transform 200ms';
  toast.style.opacity = '0';
  toast.style.transform = 'translateY(8px)';
  setTimeout(() => toast.remove(), 220);
}

/* -------------------------------------------------------------------------
   History table: client-side search + sort + status filter.
   -------------------------------------------------------------------------*/
function initHistoryTable() {
  const table = document.getElementById('hist-table');
  if (!table) return;

  const searchInput = document.getElementById('hist-search');
  const statusSelect = document.getElementById('hist-status');
  const tbody = table.querySelector('tbody');
  const allRows = Array.from(tbody.querySelectorAll('tr'));

  function applyFilters() {
    const q = (searchInput?.value || '').trim().toLowerCase();
    const status = statusSelect?.value || 'all';
    let visible = 0;

    allRows.forEach(row => {
      const target = row.dataset.target?.toLowerCase() || '';
      const id = row.dataset.id || '';
      const rowStatus = row.dataset.status || '';

      const matchQuery = !q || target.includes(q) || id.includes(q);
      const matchStatus = status === 'all' || rowStatus === status;
      const show = matchQuery && matchStatus;
      row.hidden = !show;
      if (show) visible++;
    });

    const empty = document.getElementById('hist-empty-filtered');
    if (empty) empty.hidden = visible !== 0;
  }

  searchInput?.addEventListener('input', applyFilters);
  statusSelect?.addEventListener('change', applyFilters);

  // Sort by clicking on a `<th data-sort="key">`.
  table.querySelectorAll('th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      const current = th.getAttribute('aria-sort');
      const next = current === 'ascending' ? 'descending' : 'ascending';

      table.querySelectorAll('th[data-sort]').forEach(t => t.removeAttribute('aria-sort'));
      th.setAttribute('aria-sort', next);

      const dir = next === 'ascending' ? 1 : -1;
      const sorted = allRows.slice().sort((a, b) => {
        const av = a.dataset[key] ?? '';
        const bv = b.dataset[key] ?? '';
        const an = parseFloat(av), bn = parseFloat(bv);
        const isNum = !Number.isNaN(an) && !Number.isNaN(bn);
        return isNum ? (an - bn) * dir : av.localeCompare(bv) * dir;
      });
      sorted.forEach(r => tbody.appendChild(r));
    });
  });
}

/* -------------------------------------------------------------------------
   Findings <details> rows: re-render Lucide icons inside body when opened.
   -------------------------------------------------------------------------*/
function initFindingExpand() {
  document.querySelectorAll('.finding').forEach(detail => {
    detail.addEventListener('toggle', () => {
      if (detail.open && window.lucide) {
        lucide.createIcons({ nodes: [detail] });
      }
    });
  });
}

/* -------------------------------------------------------------------------
   Delete scan, exposed globally so onclick="deleteScan(N)" still works.
   -------------------------------------------------------------------------*/
function exposeDeleteScan() {
  window.deleteScan = function (scanId, btn) {
    if (!confirm('Delete scan #' + scanId + '? This cannot be undone.')) return;
    fetch('/history/' + scanId, { method: 'DELETE' })
      .then(r => { if (!r.ok) throw new Error('Delete failed'); return r.json(); })
      .then(() => {
        const row = document.querySelector('tr[data-id="' + scanId + '"]');
        if (row) {
          row.style.transition = 'opacity 200ms, transform 200ms';
          row.style.opacity = '0';
          row.style.transform = 'translateX(-12px)';
          setTimeout(() => row.remove(), 220);
        }
      })
      .catch(err => alert('Failed to delete scan: ' + err.message));
  };
}
