// Kafem Main JavaScript

// Toast notification function
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Image preview for file uploads
function previewImage(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);
    
    if (file && preview) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Auto-refresh for waiter dashboard
function startAutoRefresh(url, interval = 30000) {
    setInterval(() => {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                updateOrderCounts(data);
            })
            .catch(error => console.error('Auto-refresh error:', error));
    }, interval);
}

function updateOrderCounts(data) {
    const pendingBadge = document.getElementById('pending-count');
    const preparingBadge = document.getElementById('preparing-count');
    
    if (pendingBadge) pendingBadge.textContent = data.pending;
    if (preparingBadge) preparingBadge.textContent = data.preparing;
}

// Format currency
function formatCurrency(amount) {
    return parseFloat(amount).toFixed(2) + ' ₼';
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('az-AZ') + ' ' + date.toLocaleTimeString('az-AZ', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Panoya kopyalandı', 'success');
    }).catch(err => {
        showToast('Kopyalama xətası', 'error');
    });
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Çap</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        body { font-family: Arial, sans-serif; }
                        @media print { body { margin: 0; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        printWindow.close();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // File input change handlers
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.dataset.preview;
            if (previewId) {
                previewImage(this, previewId);
            }
        });
    });
    
    // Auto-refresh for waiter dashboard
    if (window.location.pathname.includes('/waiter/dashboard')) {
        startAutoRefresh('/waiter/api/orders/status');
    }
});