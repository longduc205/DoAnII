/**
 * AI Web Vulnerability Scanner — Frontend Logic
 * Handles: scan form submission, progress overlay, history search, delete
 */

document.addEventListener('DOMContentLoaded', () => {
    initScanForm();
    initQuickScanForm();
    initHistorySearch();
});

/* ============================================
   Scan Form + Progress Overlay
   ============================================ */
function initScanForm() {
    const form = document.getElementById('scan-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const targetUrl = document.getElementById('target_url').value;
        if (!targetUrl) return;

        showScanOverlay(targetUrl);
        simulateScanProgress(form);
    });

    const cancelBtn = document.getElementById('btn-cancel-scan');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', hideScanOverlay);
    }
}

function showScanOverlay(targetUrl) {
    const overlay = document.getElementById('scan-overlay');
    const targetDisplay = document.getElementById('scan-target-display');
    if (!overlay) return;

    targetDisplay.textContent = `Target: ${targetUrl}`;
    overlay.classList.add('active');

    // Reset steps
    document.querySelectorAll('.scan-step').forEach(step => {
        step.className = 'scan-step scan-step--pending';
        step.querySelector('.scan-step-icon').textContent = '○';
    });

    // Reset progress
    const progressFill = document.getElementById('scan-progress-fill');
    if (progressFill) progressFill.style.width = '0%';
}

function hideScanOverlay() {
    const overlay = document.getElementById('scan-overlay');
    if (overlay) overlay.classList.remove('active');
}

function simulateScanProgress(form) {
    const steps = ['crawl', 'sqli', 'xss', 'ai'];
    const progressFill = document.getElementById('scan-progress-fill');
    let currentStep = 0;

    function advanceStep() {
        if (currentStep > 0) {
            const prevStep = document.querySelector(`[data-step="${steps[currentStep - 1]}"]`);
            if (prevStep) {
                prevStep.className = 'scan-step scan-step--done';
                prevStep.querySelector('.scan-step-icon').textContent = '✅';
            }
        }

        if (currentStep < steps.length) {
            const step = document.querySelector(`[data-step="${steps[currentStep]}"]`);
            if (step) {
                step.className = 'scan-step scan-step--active';
                step.querySelector('.scan-step-icon').textContent = '🔄';
            }
            const pct = ((currentStep + 1) / steps.length) * 100;
            if (progressFill) progressFill.style.width = `${pct}%`;

            currentStep++;
            setTimeout(advanceStep, 800 + Math.random() * 600);
        } else {
            // All steps done — submit the form normally
            setTimeout(() => {
                hideScanOverlay();
                form.submit();
            }, 500);
        }
    }

    setTimeout(advanceStep, 300);
}

/* ============================================
   Quick Scan (Dashboard)
   ============================================ */
function initQuickScanForm() {
    const form = document.getElementById('quick-scan-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const targetUrl = form.querySelector('input[name="target_url"]').value;
        if (!targetUrl) return;

        // Redirect to scan page with URL pre-filled, then auto-submit
        const scanUrl = new URL(form.action);
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.href = response.url;
            }
        }).catch(() => {
            form.submit();
        });
    });
}

/* ============================================
   History Search Filter
   ============================================ */
function initHistorySearch() {
    const searchInput = document.getElementById('history-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#history-table tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}

/* ============================================
   Delete Scan
   ============================================ */
function deleteScan(scanId) {
    if (!confirm(`Delete scan #${scanId}? This action cannot be undone.`)) return;

    // TODO: Send DELETE request to server when route is implemented
    // fetch(`/history/${scanId}`, { method: 'DELETE' })

    // For now, remove the row from the table visually
    const row = document.querySelector(`tr[data-scan-id="${scanId}"]`);
    if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'all 0.3s ease';
        setTimeout(() => row.remove(), 300);
    }
}
