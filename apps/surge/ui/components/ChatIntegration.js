/**
 * Chat Integration Component
 * Provides UI for Chatwoot and Discord chat features
 */

class ChatIntegration {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            showChatwoot: options.showChatwoot !== false,
            showDiscord: options.showDiscord !== false,
            autoConnect: options.autoConnect !== false,
            position: options.position || 'bottom-right',
            theme: options.theme || 'light',
            ...options
        };
        
        this.isConnected = {
            chatwoot: false,
            discord: false
        };
        
        this.stats = {
            chatwoot: { conversations: 0, status: 'disconnected' },
            discord: { members: 0, status: 'disconnected' }
        };
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="chat-integration ${this.options.theme}" data-component="chat-integration">
                ${this.renderHeader()}
                ${this.renderChatOptions()}
                ${this.renderStats()}
                ${this.renderChatWidget()}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
        
        if (this.options.autoConnect) {
            this.initializeConnections();
        }
    }

    renderHeader() {
        return `
            <div class="chat-header flex justify-between items-center p-4 bg-blue-50 border-b">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">Chat Support</h3>
                    <p class="text-sm text-gray-600">Connect with our team</p>
                </div>
                <div class="flex items-center space-x-2">
                    ${this.renderConnectionStatus()}
                    <button class="refresh-stats-btn p-2 text-blue-600 hover:bg-blue-100 rounded">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    renderConnectionStatus() {
        const chatwootStatus = this.isConnected.chatwoot ? 'connected' : 'disconnected';
        const discordStatus = this.isConnected.discord ? 'connected' : 'disconnected';
        
        return `
            <div class="connection-status flex items-center space-x-2">
                <div class="status-indicator ${chatwootStatus}" title="Chatwoot: ${chatwootStatus}">
                    <div class="w-2 h-2 rounded-full ${this.isConnected.chatwoot ? 'bg-green-500' : 'bg-red-500'}"></div>
                </div>
                <div class="status-indicator ${discordStatus}" title="Discord: ${discordStatus}">
                    <div class="w-2 h-2 rounded-full ${this.isConnected.discord ? 'bg-green-500' : 'bg-red-500'}"></div>
                </div>
            </div>
        `;
    }

    renderChatOptions() {
        const options = [];
        
        if (this.options.showChatwoot) {
            options.push(`
                <div class="chat-option chatwoot-option p-4 border rounded-lg bg-white hover:bg-gray-50 cursor-pointer">
                    <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="flex-1">
                            <h4 class="text-md font-medium text-gray-900">Live Chat</h4>
                            <p class="text-sm text-gray-500">Get immediate help from our support team</p>
                            <div class="text-xs text-gray-400 mt-1">
                                ${this.stats.chatwoot.conversations} active conversations
                            </div>
                        </div>
                        <div class="connection-badge ${this.isConnected.chatwoot ? 'connected' : 'disconnected'}">
                            ${this.isConnected.chatwoot ? 'Online' : 'Offline'}
                        </div>
                    </div>
                </div>
            `);
        }
        
        if (this.options.showDiscord) {
            options.push(`
                <div class="chat-option discord-option p-4 border rounded-lg bg-white hover:bg-gray-50 cursor-pointer">
                    <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                            <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                                <svg class="w-6 h-6 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419-.0189 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1568 2.4189Z"/>
                                </svg>
                            </div>
                        </div>
                        <div class="flex-1">
                            <h4 class="text-md font-medium text-gray-900">Discord Community</h4>
                            <p class="text-sm text-gray-500">Join our Discord server for community support</p>
                            <div class="text-xs text-gray-400 mt-1">
                                ${this.stats.discord.members} members online
                            </div>
                        </div>
                        <div class="connection-badge ${this.isConnected.discord ? 'connected' : 'disconnected'}">
                            ${this.isConnected.discord ? 'Online' : 'Offline'}
                        </div>
                    </div>
                </div>
            `);
        }
        
        return `
            <div class="chat-options space-y-3 p-4">
                ${options.join('')}
            </div>
        `;
    }

    renderStats() {
        return `
            <div class="chat-stats p-4 bg-gray-50 border-t">
                <h4 class="text-sm font-medium text-gray-700 mb-2">Platform Status</h4>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="stat-item">
                        <div class="font-medium text-blue-600">Chatwoot</div>
                        <div class="text-gray-600">${this.stats.chatwoot.status}</div>
                        <div class="text-xs text-gray-500">${this.stats.chatwoot.conversations} conversations</div>
                    </div>
                    <div class="stat-item">
                        <div class="font-medium text-indigo-600">Discord</div>
                        <div class="text-gray-600">${this.stats.discord.status}</div>
                        <div class="text-xs text-gray-500">${this.stats.discord.members} members</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderChatWidget() {
        return `
            <div class="chat-widget-container" id="${this.containerId}-widget" style="display: none;">
                <!-- Chatwoot widget will be injected here -->
                <div id="chatwoot-widget"></div>
                
                <!-- Discord invite widget -->
                <div id="discord-invite" class="p-4 bg-indigo-50 border-t" style="display: none;">
                    <h4 class="font-medium text-indigo-900 mb-2">Join Our Discord</h4>
                    <p class="text-sm text-indigo-700 mb-3">Connect with the Surgify community</p>
                    <button class="discord-join-btn w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors">
                        Join Discord Server
                    </button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Refresh stats button
        const refreshBtn = container.querySelector('.refresh-stats-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStats());
        }

        // Chatwoot option click
        const chatwootOption = container.querySelector('.chatwoot-option');
        if (chatwootOption) {
            chatwootOption.addEventListener('click', () => this.openChatwoot());
        }

        // Discord option click
        const discordOption = container.querySelector('.discord-option');
        if (discordOption) {
            discordOption.addEventListener('click', () => this.openDiscord());
        }

        // Discord join button
        const discordJoinBtn = container.querySelector('.discord-join-btn');
        if (discordJoinBtn) {
            discordJoinBtn.addEventListener('click', () => this.joinDiscord());
        }
    }

    async initializeConnections() {
        try {
            // Test backend connections
            const response = await fetch('/api/v1/chat/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateConnectionStatus(stats);
            }
        } catch (error) {
            console.error('Failed to initialize chat connections:', error);
        }
    }

    async refreshStats() {
        try {
            const response = await fetch('/api/v1/chat/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateConnectionStatus(stats);
                this.updateStatsDisplay();
            }
        } catch (error) {
            console.error('Failed to refresh chat stats:', error);
        }
    }

    updateConnectionStatus(stats) {
        this.isConnected.chatwoot = stats.chatwoot?.status === 'connected';
        this.isConnected.discord = stats.discord?.status === 'connected';
        this.stats = stats;
        
        // Update UI
        this.updateConnectionIndicators();
    }

    updateConnectionIndicators() {
        const container = document.getElementById(this.containerId);
        
        // Update connection dots
        const chatwootIndicator = container.querySelector('.status-indicator.chatwoot');
        const discordIndicator = container.querySelector('.status-indicator.discord');
        
        if (chatwootIndicator) {
            const dot = chatwootIndicator.querySelector('.w-2');
            dot.className = `w-2 h-2 rounded-full ${this.isConnected.chatwoot ? 'bg-green-500' : 'bg-red-500'}`;
        }
        
        if (discordIndicator) {
            const dot = discordIndicator.querySelector('.w-2');
            dot.className = `w-2 h-2 rounded-full ${this.isConnected.discord ? 'bg-green-500' : 'bg-red-500'}`;
        }
    }

    updateStatsDisplay() {
        const container = document.getElementById(this.containerId);
        const statsSection = container.querySelector('.chat-stats');
        if (statsSection) {
            statsSection.outerHTML = this.renderStats();
        }
    }

    async openChatwoot() {
        if (!this.isConnected.chatwoot) {
            alert('Chatwoot is currently offline. Please try again later.');
            return;
        }

        try {
            // Load Chatwoot widget
            this.loadChatwootWidget();
        } catch (error) {
            console.error('Failed to open Chatwoot:', error);
        }
    }

    loadChatwootWidget() {
        // Load Chatwoot script dynamically
        if (!window.$chatwoot) {
            const script = document.createElement('script');
            script.src = 'https://widget.chatwoot.com/init.js';
            script.async = true;
            document.head.appendChild(script);

            script.onload = () => {
                // Initialize Chatwoot widget
                window.chatwootSDK.run({
                    websiteToken: 'your-website-token', // This should come from config
                    baseUrl: 'https://app.chatwoot.com'
                });
            };
        } else {
            // Widget already loaded, just show it
            window.$chatwoot.toggle();
        }
    }

    async openDiscord() {
        const container = document.getElementById(this.containerId);
        const discordInvite = container.querySelector('#discord-invite');
        
        if (discordInvite) {
            discordInvite.style.display = discordInvite.style.display === 'none' ? 'block' : 'none';
        }
    }

    async joinDiscord() {
        try {
            // Get Discord invite link from backend
            const response = await fetch('/api/v1/chat/discord/invite', {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.invite_url) {
                    window.open(data.invite_url, '_blank');
                } else {
                    alert('Unable to generate Discord invite. Please contact support.');
                }
            } else {
                alert('Discord service is currently unavailable.');
            }
        } catch (error) {
            console.error('Failed to join Discord:', error);
            alert('Failed to join Discord. Please try again later.');
        }
    }

    // Public methods
    setConnectionStatus(platform, status) {
        this.isConnected[platform] = status;
        this.updateConnectionIndicators();
    }

    updateStats(newStats) {
        this.stats = { ...this.stats, ...newStats };
        this.updateStatsDisplay();
    }

    destroy() {
        // Clean up Chatwoot widget if loaded
        if (window.$chatwoot) {
            window.$chatwoot.hide();
        }
    }
}

// Export for use in other modules
window.ChatIntegration = ChatIntegration;
