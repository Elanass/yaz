/**
 * InteractionIsland Component - Simplified feedback component
 */

class InteractionIsland {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            title: options.title || 'Feedback Hub',
            endpoint: options.endpoint || '/api/feedback',
            placeholder: options.placeholder || 'Share your feedback or suggestions...',
            ...options
        };
        
        this.entries = [];
    }

    async render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="interaction-island bg-white rounded-lg shadow-sm border border-gray-200 p-6" data-component="interaction-island">
                <div class="mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">${this.options.title}</h3>
                    <p class="text-gray-600 text-sm mt-1">Share your thoughts and help improve our services</p>
                </div>
                
                <form id="feedback-form" class="space-y-4">
                    <textarea 
                        id="feedback-content" 
                        rows="3" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none" 
                        placeholder="${this.options.placeholder}"
                        maxlength="300"
                    ></textarea>
                    
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-gray-500">
                            <span id="char-count">0</span>/300 characters
                        </span>
                        <button 
                            type="submit" 
                            id="submit-btn"
                            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                            disabled
                        >
                            Submit
                        </button>
                    </div>
                </form>
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
    }

    attachEventListeners() {
        const form = document.getElementById('feedback-form');
        const textarea = document.getElementById('feedback-content');
        const charCount = document.getElementById('char-count');
        const submitBtn = document.getElementById('submit-btn');

        if (textarea && charCount && submitBtn) {
            textarea.addEventListener('input', () => {
                const length = textarea.value.length;
                charCount.textContent = length;
                submitBtn.disabled = length === 0 || length > 300;
            });

            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const content = document.getElementById('feedback-content').value.trim();
        if (!content) return;

        const submitBtn = document.getElementById('submit-btn');
        const originalText = submitBtn.textContent;
        
        try {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            await this.submitFeedback({ content });
            
            document.getElementById('feedback-form').reset();
            document.getElementById('char-count').textContent = '0';
            
            this.showNotification('Feedback submitted successfully!', 'success');
            
        } catch (error) {
            console.error('Submission error:', error);
            this.showNotification('Failed to submit feedback. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async submitFeedback(data) {
        // Simulate API call - replace with actual implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ success: true });
            }, 1000);
        });
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            info: 'bg-blue-600'
        };
        
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InteractionIsland;
} else {
    window.InteractionIsland = InteractionIsland;
}
