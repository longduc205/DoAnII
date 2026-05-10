/**
 * Sentinel Scanner, frontend behavior.
 * Scoped, dependency-free. Only wires up what server-rendered HTML needs.
 */

document.addEventListener('DOMContentLoaded', () => {
  initScanForm();
  initToasts();
  initHistoryTable();
  initFindingExpand();
  initCustomSelects();
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
   History table: Handle server-side filter form submission.
   -------------------------------------------------------------------------*/
function initHistoryTable() {
  const form = document.getElementById('history-filter-form');
  if (!form) return;

  const statusSelect = document.getElementById('hist-status');

  // Auto-submit form when status changes
  statusSelect?.addEventListener('change', () => {
    form.submit();
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
   Custom Selects: transform native `<select>` into a custom-styled dropdown.
   Matches the "Sentinel's Ledger" theme with rounded corners and glows.
   -------------------------------------------------------------------------*/
function initCustomSelects() {
  document.querySelectorAll('.custom-select').forEach(container => {
    const nativeSelect = container.querySelector('select');
    const trigger = container.querySelector('.custom-select-trigger');
    const triggerText = trigger.querySelector('span');
    const list = container.querySelector('.custom-select-list');
    const options = Array.from(container.querySelectorAll('.custom-select-option'));

    if (!nativeSelect || !trigger || !list) return;

    // Toggle dropdown
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = container.classList.toggle('is-open');
      
      // Close other open selects
      document.querySelectorAll('.custom-select').forEach(other => {
        if (other !== container) other.classList.remove('is-open');
      });
    });

    // Handle option selection
    options.forEach(opt => {
      opt.addEventListener('click', () => {
        const value = opt.dataset.value;
        const label = opt.textContent;

        // Update native select
        nativeSelect.value = value;
        nativeSelect.dispatchEvent(new Event('change'));

        // Update UI
        triggerText.textContent = label;
        options.forEach(o => o.classList.remove('is-selected'));
        opt.classList.add('is-selected');

        container.classList.remove('is-open');
      });
    });
  });

  // Close when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select').forEach(c => c.classList.remove('is-open'));
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
