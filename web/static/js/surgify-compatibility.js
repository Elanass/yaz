/**
 * Surgify UI Compatibility & Enhancement Module
 * 
 * Enhances your existing Surgify interface with:
 * - DRY component behaviors
 * - Cross-component compatibility
 * - Unified event handling
 * - Enhanced UX patterns
 */

// Surgify UI Enhancement Namespace
window.SurgifyUI = window.SurgifyUI || {};

/**
 * Card System Enhancement
 */
SurgifyUI.cards = {
    /**
     * Initialize enhanced card behaviors
     */
    init: () => {
        // Add hover effects to all cards
        document.querySelectorAll('.surgify-card, .surgify-event-card').forEach(card => {
            SurgifyUI.cards.enhanceCard(card);
        });
    },

    /**
     * Enhance individual card
     */
    enhanceCard: (card) => {
        // Add smooth transitions
        card.style.transition = 'all 0.2s ease';
        
        // Add click ripple effect
        card.addEventListener('click', (e) => {
            if (!card.classList.contains('no-ripple')) {
                SurgifyUI.effects.createRipple(e, card);
            }
        });
        
        // Add keyboard navigation
        if (card.querySelector('a')) {
            card.setAttribute('tabindex', '0');
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const link = card.querySelector('a');
                    if (link) link.click();
                }
            });
        }
    }
};

/**
 * Button System Enhancement
 */
SurgifyUI.buttons = {
    /**
     * Initialize enhanced button behaviors
     */
    init: () => {
        document.querySelectorAll('.surgify-btn').forEach(btn => {
            SurgifyUI.buttons.enhanceButton(btn);
        });
    },

    /**
     * Enhance individual button
     */
    enhanceButton: (btn) => {
        // Add loading state capability
        btn.setAttribute('data-original-text', btn.innerHTML);
        
        // Add click handler for loading state
        btn.addEventListener('click', function(e) {
            if (this.dataset.loading === 'true') {
                e.preventDefault();
                return false;
            }
        });
    },

    /**
     * Set button loading state
     */
    setLoading: (btn, loading = true) => {
        if (loading) {
            btn.dataset.loading = 'true';
            btn.disabled = true;
            btn.innerHTML = `
                <svg class="surgify-spinner" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="60" stroke-dashoffset="60">
                        <animate attributeName="stroke-dashoffset" dur="2s" values="60;0" repeatCount="indefinite"/>
                    </circle>
                </svg>
                Loading...
            `;
        } else {
            btn.dataset.loading = 'false';
            btn.disabled = false;
            btn.innerHTML = btn.getAttribute('data-original-text');
        }
    }
};

/**
 * Form Enhancement
 */
SurgifyUI.forms = {
    /**
     * Initialize enhanced form behaviors
     */
    init: () => {
        document.querySelectorAll('.surgify-input, .surgify-select').forEach(input => {
            SurgifyUI.forms.enhanceInput(input);
        });
        
        document.querySelectorAll('form').forEach(form => {
            SurgifyUI.forms.enhanceForm(form);
        });
    },

    /**
     * Enhance individual input
     */
    enhanceInput: (input) => {
        // Add floating labels if needed
        if (input.dataset.floatingLabel) {
            SurgifyUI.forms.addFloatingLabel(input);
        }
        
        // Add validation styling
        input.addEventListener('invalid', () => {
            input.classList.add('border-red-500', 'bg-red-50');
        });
        
        input.addEventListener('input', () => {
            input.classList.remove('border-red-500', 'bg-red-50');
        });
    },

    /**
     * Enhance form with AJAX submission
     */
    enhanceForm: (form) => {
        if (form.dataset.ajax === 'true') {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await SurgifyUI.forms.submitForm(form);
            });
        }
    },

    /**
     * Submit form via AJAX
     */
    submitForm: async (form) => {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            SurgifyUI.buttons.setLoading(submitBtn, true);
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action || window.location.href, {
                method: form.method || 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                SharedUtils.notifications.success(result.message || 'Form submitted successfully');
                
                if (result.redirect) {
                    window.location.href = result.redirect;
                }
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            SharedUtils.notifications.error('An error occurred. Please try again.');
        } finally {
            if (submitBtn) {
                SurgifyUI.buttons.setLoading(submitBtn, false);
            }
        }
    }
};

/**
 * Navigation Enhancement
 */
SurgifyUI.navigation = {
    /**
     * Initialize enhanced navigation
     */
    init: () => {
        // Enhance nav items
        document.querySelectorAll('.surgify-nav-item').forEach(item => {
            SurgifyUI.navigation.enhanceNavItem(item);
        });
        
        // Set active states
        SurgifyUI.navigation.setActiveStates();
    },

    /**
     * Enhance navigation item
     */
    enhanceNavItem: (item) => {
        item.addEventListener('click', function(e) {
            // Remove active from siblings
            this.parentElement.querySelectorAll('.surgify-nav-item').forEach(sibling => {
                sibling.classList.remove('active');
            });
            
            // Add active to current
            this.classList.add('active');
        });
    },

    /**
     * Set active states based on current URL
     */
    setActiveStates: () => {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.surgify-nav-item').forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                item.classList.add('active');
            }
        });
    }
};

/**
 * Effects and Animations
 */
SurgifyUI.effects = {
    /**
     * Create ripple effect on click
     */
    createRipple: (event, element) => {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: surgify-ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 1;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    },

    /**
     * Smooth scroll to element
     */
    smoothScrollTo: (target, offset = 80) => {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element) {
            const elementPosition = element.offsetTop - offset;
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    },

    /**
     * Fade in animation
     */
    fadeIn: (element, duration = 300) => {
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms ease`;
        element.style.display = 'block';
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
        });
    }
};

/**
 * Layout Enhancements
 */
SurgifyUI.layout = {
    /**
     * Initialize responsive behaviors
     */
    init: () => {
        SurgifyUI.layout.handleResize();
        window.addEventListener('resize', SharedUtils.utils.debounce(SurgifyUI.layout.handleResize, 250));
    },

    /**
     * Handle responsive layout changes
     */
    handleResize: () => {
        const width = window.innerWidth;
        
        // Update mobile navigation
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && width > 1024) {
            sidebar.classList.remove('sidebar-open');
        }
        
        // Update event carousel
        const carousel = document.querySelector('.events-carousel');
        if (carousel) {
            SurgifyUI.layout.updateCarousel(carousel, width);
        }
    },

    /**
     * Update carousel for current viewport
     */
    updateCarousel: (carousel, width) => {
        const cards = carousel.querySelectorAll('.surgify-event-card');
        const cardWidth = width < 640 ? width - 40 : 320; // 20rem = 320px
        
        cards.forEach(card => {
            card.style.width = `${cardWidth}px`;
        });
    }
};

/**
 * Data Loading and States
 */
SurgifyUI.data = {
    /**
     * Load data with loading states
     */
    loadData: async (url, container, options = {}) => {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'surgify-loading';
        loadingEl.innerHTML = `
            <div class="surgify-spinner"></div>
            <span>Loading...</span>
        `;
        
        if (container) {
            container.innerHTML = '';
            container.appendChild(loadingEl);
        }
        
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            
            if (container) {
                container.removeChild(loadingEl);
            }
            
            return data;
        } catch (error) {
            if (container) {
                container.innerHTML = `
                    <div class="surgify-alert surgify-alert-error">
                        <span>Failed to load data. Please try again.</span>
                    </div>
                `;
            }
            throw error;
        }
    }
};

/**
 * Initialize all Surgify UI enhancements
 */
SurgifyUI.init = () => {
    console.log('🎨 Initializing Surgify UI enhancements...');
    
    // Initialize all modules
    SurgifyUI.cards.init();
    SurgifyUI.buttons.init();
    SurgifyUI.forms.init();
    SurgifyUI.navigation.init();
    SurgifyUI.layout.init();
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes surgify-ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .surgify-fade-in {
            animation: surgify-fade-in 0.3s ease forwards;
        }
        
        @keyframes surgify-fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Surgify UI enhancements initialized');
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', SurgifyUI.init);
} else {
    SurgifyUI.init();
}

// Export for manual initialization
window.SurgifyUI = SurgifyUI;
