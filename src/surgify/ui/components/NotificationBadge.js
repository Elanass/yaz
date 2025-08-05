/**
 * NotificationBadge Component
 * A reusable notification badge component with real-time updates and htmx support
 */

class NotificationBadge {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            count: options.count || 0,
            maxCount: options.maxCount || 99,
            showZero: options.showZero === true,
            type: options.type || 'default', // default, primary, success, warning, danger
            size: options.size || 'medium', // small, medium, large
            position: options.position || 'top-right', // top-right, top-left, bottom-right, bottom-left
            animated: options.animated !== false,
            onClick: options.onClick || null,
            htmxEndpoint: options.htmxEndpoint || null,
            autoUpdate: options.autoUpdate === true,
            updateInterval: options.updateInterval || 30000, // 30 seconds
            className: options.className || '',
            ...options
        };
        this.updateTimer = null;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const shouldShow = this.options.count > 0 || this.options.showZero;
        const displayCount = this.options.count > this.options.maxCount 
            ? `${this.options.maxCount}+` 
            : this.options.count.toString();

        const typeClasses = {
            default: 'bg-gray-500 text-white',
            primary: 'bg-blue-500 text-white',
            success: 'bg-green-500 text-white',
            warning: 'bg-yellow-500 text-white',
            danger: 'bg-red-500 text-white'
        };

        const sizeClasses = {
            small: 'text-xs px-1.5 py-0.5 min-w-[16px] h-4',
            medium: 'text-xs px-2 py-1 min-w-[20px] h-5',
            large: 'text-sm px-2.5 py-1 min-w-[24px] h-6'
        };

        const positionClasses = {
            'top-right': '-top-1 -right-1',
            'top-left': '-top-1 -left-1',
            'bottom-right': '-bottom-1 -right-1',
            'bottom-left': '-bottom-1 -left-1'
        };

        const html = `
            <div class="notification-badge relative inline-block ${this.options.className}" data-component="notification-badge">
                ${container.innerHTML}
                ${shouldShow ? `
                    <span 
                        class="badge absolute ${positionClasses[this.options.position]} inline-flex items-center justify-center ${sizeClasses[this.options.size]} ${typeClasses[this.options.type]} font-medium rounded-full border-2 border-white ${this.options.animated ? 'transition-all duration-300 ease-in-out' : ''}"
                        data-count="${this.options.count}"
                        ${this.options.htmxEndpoint ? `hx-get="${this.options.htmxEndpoint}" hx-trigger="click"` : ''}
                    >
                        ${displayCount}
                    </span>
                ` : ''}
            </div>
        `;

        container.outerHTML = html;
        this.attachEventListeners();
        
        if (this.options.autoUpdate) {
            this.startAutoUpdate();
        }
    }

    attachEventListeners() {
        const container = document.querySelector(`[data-component="notification-badge"]`);
        if (!container) return;

        const badge = container.querySelector('.badge');
        if (badge && this.options.onClick) {
            badge.addEventListener('click', (e) => {
                e.preventDefault();
                this.options.onClick(this.options.count);
            });
        }

        // Handle badge animations
        if (badge && this.options.animated) {
            badge.addEventListener('transitionend', () => {
                // Animation completed
            });
        }
    }

    // Public methods
    setCount(count) {
        const oldCount = this.options.count;
        this.options.count = Math.max(0, parseInt(count) || 0);
        
        const container = document.querySelector(`[data-component="notification-badge"]`);
        if (!container) {
            this.render();
            return;
        }

        this.updateBadgeDisplay(oldCount);
        
        // Dispatch custom event
        container.dispatchEvent(new CustomEvent('countChanged', {
            detail: { 
                oldCount, 
                newCount: this.options.count,
                increased: this.options.count > oldCount 
            },
            bubbles: true
        }));
    }

    updateBadgeDisplay(oldCount) {
        const container = document.querySelector(`[data-component="notification-badge"]`);
        if (!container) return;

        let badge = container.querySelector('.badge');
        const shouldShow = this.options.count > 0 || this.options.showZero;
        const displayCount = this.options.count > this.options.maxCount 
            ? `${this.options.maxCount}+` 
            : this.options.count.toString();

        if (shouldShow) {
            if (badge) {
                // Update existing badge
                badge.textContent = displayCount;
                badge.setAttribute('data-count', this.options.count);
                
                // Add pulse animation for increases
                if (this.options.animated && this.options.count > oldCount) {
                    badge.classList.add('animate-pulse');
                    setTimeout(() => {
                        badge.classList.remove('animate-pulse');
                    }, 1000);
                }
            } else {
                // Create new badge
                this.render();
            }
        } else {
            // Hide badge
            if (badge) {
                if (this.options.animated) {
                    badge.style.transform = 'scale(0)';
                    badge.style.opacity = '0';
                    setTimeout(() => {
                        badge.remove();
                    }, 300);
                } else {
                    badge.remove();
                }
            }
        }
    }

    increment(amount = 1) {
        this.setCount(this.options.count + amount);
    }

    decrement(amount = 1) {
        this.setCount(this.options.count - amount);
    }

    reset() {
        this.setCount(0);
    }

    getCount() {
        return this.options.count;
    }

    setType(type) {
        if (['default', 'primary', 'success', 'warning', 'danger'].includes(type)) {
            this.options.type = type;
            this.render();
        }
    }

    setSize(size) {
        if (['small', 'medium', 'large'].includes(size)) {
            this.options.size = size;
            this.render();
        }
    }

    setPosition(position) {
        const validPositions = ['top-right', 'top-left', 'bottom-right', 'bottom-left'];
        if (validPositions.includes(position)) {
            this.options.position = position;
            this.render();
        }
    }

    // Auto-update functionality
    startAutoUpdate() {
        if (this.options.htmxEndpoint && !this.updateTimer) {
            this.updateTimer = setInterval(() => {
                this.fetchUpdatedCount();
            }, this.options.updateInterval);
        }
    }

    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    async fetchUpdatedCount() {
        if (!this.options.htmxEndpoint) return;

        try {
            const response = await fetch(this.options.htmxEndpoint);
            if (response.ok) {
                const data = await response.json();
                if (typeof data.count !== 'undefined') {
                    this.setCount(data.count);
                }
            }
        } catch (error) {
            console.error('Failed to fetch updated count:', error);
        }
    }

    // Cleanup
    destroy() {
        this.stopAutoUpdate();
        const container = document.querySelector(`[data-component="notification-badge"]`);
        if (container) {
            // Remove event listeners and restore original content
            const originalContent = container.innerHTML.replace(/<span class="badge.*?<\/span>/, '');
            container.innerHTML = originalContent;
            container.removeAttribute('data-component');
            container.className = container.className.replace('notification-badge', '').trim();
        }
    }
}

// Utility function to create multiple notification badges
function createNotificationBadges(configs) {
    const badges = {};
    
    configs.forEach(config => {
        if (config.containerId) {
            badges[config.containerId] = new NotificationBadge(config.containerId, config);
            badges[config.containerId].render();
        }
    });
    
    return badges;
}

// HTMX integration
document.addEventListener('htmx:afterRequest', function(event) {
    const badges = document.querySelectorAll('[data-component="notification-badge"]');
    badges.forEach(badge => {
        // Handle updates from HTMX
        const response = event.detail.xhr.response;
        if (response) {
            try {
                const data = JSON.parse(response);
                if (typeof data.count !== 'undefined') {
                    const badgeElement = badge.querySelector('.badge');
                    if (badgeElement) {
                        // Find the associated NotificationBadge instance and update it
                        // This would need proper instance management in a real implementation
                    }
                }
            } catch (e) {
                // Response is not JSON, ignore
            }
        }
    });
});

// WebSocket integration for real-time updates
function connectNotificationWebSocket(badges, wsUrl) {
    if (!window.WebSocket) return;

    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'notification_update' && data.badge_id && badges[data.badge_id]) {
                badges[data.badge_id].setCount(data.count);
            }
        } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
        }
    };

    ws.onclose = function() {
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
            connectNotificationWebSocket(badges, wsUrl);
        }, 5000);
    };

    return ws;
}

// CSS animations (to be included in CSS file)
const notificationBadgeStyles = `
.notification-badge .badge {
    transition: all 0.3s ease-in-out;
    transform-origin: center;
}

.notification-badge .badge.animate-pulse {
    animation: badge-pulse 1s ease-in-out;
}

@keyframes badge-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}

.notification-badge .badge:hover {
    transform: scale(1.1);
}
`;

// Inject styles if not already present
if (!document.getElementById('notification-badge-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-badge-styles';
    style.textContent = notificationBadgeStyles;
    document.head.appendChild(style);
}

// Export for module usage
window.NotificationBadge = NotificationBadge;
window.createNotificationBadges = createNotificationBadges;
window.connectNotificationWebSocket = connectNotificationWebSocket;
