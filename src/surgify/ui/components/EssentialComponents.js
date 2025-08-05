/**
 * Essential UI Components - Disclaimer, Contact, and Ko-fi
 */

// Disclaimer Component
class DisclaimerComponent {
    constructor(containerId) {
        this.containerId = containerId;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="disclaimer bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <svg class="w-5 h-5 text-amber-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                        </svg>
                    </div>
                    <div>
                        <h4 class="text-sm font-medium text-amber-800">Medical Disclaimer</h4>
                        <p class="text-sm text-amber-700 mt-1">
                            This platform is for research and educational purposes only. All medical information and surgical recommendations must be verified by qualified healthcare professionals. Do not use this platform for emergency medical decisions.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }
}

// Contact Component
class ContactComponent {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            email: options.email || 'support@surgify.ai',
            title: options.title || 'Get in Touch',
            ...options
        };
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="contact bg-white border border-gray-200 rounded-lg p-6">
                <div class="flex items-center space-x-3 mb-4">
                    <div class="flex-shrink-0">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900">${this.options.title}</h3>
                </div>
                
                <p class="text-gray-600 text-sm mb-4">
                    Have questions, feedback, or need support? We'd love to hear from you.
                </p>
                
                <div class="flex items-center space-x-2">
                    <a 
                        href="mailto:${this.options.email}" 
                        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                        ${this.options.email}
                    </a>
                </div>
            </div>
        `;
    }
}

// Ko-fi Donation Component
class KofiComponent {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            username: options.username || 'surgify',
            title: options.title || 'Support Our Work',
            message: options.message || 'Help us maintain and improve this platform',
            ...options
        };
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="kofi-support bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
                <div class="flex items-center space-x-3 mb-4">
                    <div class="flex-shrink-0">
                        <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900">${this.options.title}</h3>
                </div>
                
                <p class="text-gray-600 text-sm mb-4">
                    ${this.options.message}. Your support helps us keep this platform free and accessible.
                </p>
                
                <div class="flex items-center space-x-3">
                    <a 
                        href="https://ko-fi.com/${this.options.username}" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105"
                    >
                        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M23.881 8.948c-.773-4.085-4.859-4.593-4.859-4.593H.723c-.604 0-.679.798-.679.798s-.082 7.324-.033 11.414c.049 4.271 2.484 7.433 8.262 7.433s8.213-3.162 8.262-7.433c.049-4.09-.033-11.414-.033-11.414s-.075-.798-.679-.798h-3.12s.73.534.73 1.798-.73 1.798-.73 1.798H6.408s.73-.534.73-1.798-.73-1.798-.73-1.798H23.1s.775.534.775 1.798-.775 1.798-.775 1.798z"/>
                        </svg>
                        Buy us a coffee
                    </a>
                    <span class="text-xs text-gray-500">
                        Powered by Ko-fi
                    </span>
                </div>
            </div>
        `;
    }
}

// Export components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DisclaimerComponent, ContactComponent, KofiComponent };
} else {
    window.DisclaimerComponent = DisclaimerComponent;
    window.ContactComponent = ContactComponent;
    window.KofiComponent = KofiComponent;
}
