/**
 * Sentinel Scanner, frontend behavior.
 * Scoped, dependency-free. Only wires up what server-rendered HTML needs.
 */

document.addEventListener('DOMContentLoaded', () => {
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
   Scan form: handled inline in scan.html (premium overlay).
   -------------------------------------------------------------------------*/


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
