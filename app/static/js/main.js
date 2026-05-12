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
  initUserDropdown();
  initNotifications();
  initCommandPalette();
  exposeDeleteScan();
});

/* -------------------------------------------------------------------------
   User Dropdown: toggle visibility of the profile menu.
   -------------------------------------------------------------------------*/
function initUserDropdown() {
  const container = document.getElementById('user-profile-dropdown');
  if (!container) return;

  const trigger = container.querySelector('.user-profile-trigger');
  if (!trigger) return;

  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    container.classList.toggle('is-open');
    // Close others
    document.getElementById('notification-wrapper')?.classList.remove('is-open');
  });

  document.addEventListener('click', (e) => {
    if (!container.contains(e.target)) {
      container.classList.remove('is-open');
    }
  });
}

/* -------------------------------------------------------------------------
   Notifications: toggle popover visibility.
   -------------------------------------------------------------------------*/
function initNotifications() {
  const wrapper = document.getElementById('notification-wrapper');
  if (!wrapper) return;

  const trigger = document.getElementById('notification-trigger');
  if (!trigger) return;

  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    wrapper.classList.toggle('is-open');
    // Close others
    document.getElementById('user-profile-dropdown')?.classList.remove('is-open');
  });

  // Mark all as read simulation
  const markReadBtn = document.getElementById('mark-all-read');
  const dot = document.getElementById('notification-dot');
  if (markReadBtn) {
    markReadBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      wrapper.querySelectorAll('.notification-item').forEach(i => i.classList.remove('unread'));
      if (dot) dot.style.display = 'none';
    });
  }

  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove('is-open');
    }
  });
}

/* -------------------------------------------------------------------------
   Command Palette: modal logic and shortcut support.
   -------------------------------------------------------------------------*/
function initCommandPalette() {
  const palette = document.getElementById('command-palette');
  const input = document.getElementById('command-palette-input');
  const trigger = document.querySelector('.header-cmd-btn');
  const items = Array.from(palette?.querySelectorAll('.command-item') || []);

  if (!palette || !input || !trigger) return;

  function open() {
    palette.classList.add('is-open');
    input.value = '';
    // Re-show all items
    items.forEach(i => i.style.display = 'flex');
    if (window.lucide) lucide.createIcons({ nodes: [palette] });
    setTimeout(() => input.focus(), 100);
  }

  function close() {
    palette.classList.remove('is-open');
  }

  trigger.addEventListener('click', open);

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      open();
    }
    if (e.key === 'Escape' && palette.classList.contains('is-open')) {
      close();
    }
  });

  palette.addEventListener('click', (e) => {
    if (e.target === palette) close();
  });

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(q) ? 'flex' : 'none';
    });
  });
}

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
    // Determine which modules are enabled to show in progress
    const enabledModules = {
      sqli: form.elements['test_sqli']?.checked,
      xss: form.elements['test_xss']?.checked,
      ai: form.elements['use_ai']?.checked
    };

    // Filter progress steps
    stepEls.forEach(step => {
      const type = step.dataset.step;
      if (type === 'crawl') return; // Always crawl
      if (!enabledModules[type]) {
        step.style.display = 'none';
        step.classList.add('is-skipped');
      } else {
        step.style.display = 'flex';
        step.classList.remove('is-skipped');
      }
    });

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

    // Only animate steps that are NOT skipped
    const visibleSteps = Array.from(stepEls).filter(s => !s.classList.contains('is-skipped'));
    animateSteps(visibleSteps, progressFill);
  });
}

/* Animate steps as a *visual estimate* while the synchronous scan runs. */
function animateSteps(visibleSteps, progressFill) {
  if (!visibleSteps.length) return;

  let idx = 0;
  const total = visibleSteps.length;

  function tick() {
    if (idx > 0) visibleSteps[idx - 1].classList.replace('step--active', 'step--done');
    if (idx < total) {
      visibleSteps[idx].classList.add('step--active');
      const pct = ((idx + 0.7) / total) * 100;
      if (progressFill) progressFill.style.width = pct + '%';
      idx++;
      
      // Dynamic delay based on step type
      const stepType = visibleSteps[idx - 1].dataset.step;
      let delay = 1200;
      if (stepType === 'crawl') delay = 1500;
      if (stepType === 'sqli') delay = 2000;
      if (stepType === 'xss') delay = 1800;
      if (stepType === 'ai') delay = 1000;

      setTimeout(tick, delay);
    } else {
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
