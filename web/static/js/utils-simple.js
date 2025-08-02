/**
 * Simple utilities - No bloat, just what's needed
 */

// Simple notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 12px 20px;
        background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
        color: white; border-radius: 4px; z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Simple form validation
function validateForm(form) {
    const errors = [];
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            errors.push(`${input.name || input.id} is required`);
            input.style.borderColor = '#f44336';
        } else {
            input.style.borderColor = '';
        }
        
        if (input.type === 'email' && input.value && !input.value.includes('@')) {
            errors.push('Invalid email format');
            input.style.borderColor = '#f44336';
        }
    });
    
    return errors;
}

// Simple AJAX helper
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
    @keyframes slideOut { from { transform: translateX(0); } to { transform: translateX(100%); } }
`;
document.head.appendChild(style);

// Export for global use
window.Utils = { showNotification, validateForm, apiCall };
