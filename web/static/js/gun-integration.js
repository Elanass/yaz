/**
 * Gun.js Integration for Gastric ADCI Platform
 * Provides real-time distributed state management and collaborative features
 */

// Initialize Gun.js
const gun = Gun(['http://localhost:8765/gun']);

// Gastric ADCI Gun.js integration
window.GastricADCI.Gun = {
    instance: gun,
    user: null,
    collaborativeSpaces: {},
    
    /**
     * Initialize Gun.js integration
     */
    init() {
        console.log('Initializing Gun.js integration');
        
        // Setup user authentication
        this.setupAuthentication();
        
        // Setup collaborative features
        this.setupCollaboration();
        
        // Setup real-time sync
        this.setupRealtimeSync();
        
        // Setup offline resilience
        this.setupOfflineSync();
    },
    
    /**
     * Setup Gun.js user authentication
     */
    setupAuthentication() {
        this.user = gun.user();
        
        // Auto-login if credentials are stored
        const storedCredentials = localStorage.getItem('gastric_adci_gun_credentials');
        if (storedCredentials) {
            const { username, password } = JSON.parse(storedCredentials);
            this.login(username, password);
        }
    },
    
    /**
     * Login user with Gun.js
     */
    async login(username, password) {
        return new Promise((resolve, reject) => {
            this.user.auth(username, password, (ack) => {
                if (ack.err) {
                    console.error('Gun.js login failed:', ack.err);
                    reject(ack.err);
                } else {
                    console.log('Gun.js login successful');
                    
                    // Store credentials for auto-login
                    localStorage.setItem('gastric_adci_gun_credentials', 
                        JSON.stringify({ username, password }));
                    
                    // Initialize user-specific features
                    this.initializeUserFeatures();
                    
                    resolve(ack);
                }
            });
        });
    },
    
    /**
     * Create new Gun.js user account
     */
    async createUser(username, password, profile = {}) {
        return new Promise((resolve, reject) => {
            this.user.create(username, password, (ack) => {
                if (ack.err) {
                    console.error('Gun.js user creation failed:', ack.err);
                    reject(ack.err);
                } else {
                    console.log('Gun.js user created successfully');
                    
                    // Login after creation
                    this.login(username, password).then(() => {
                        // Set user profile
                        this.user.get('profile').put(profile);
                        resolve(ack);
                    });
                }
            });
        });
    },
    
    /**
     * Logout user
     */
    logout() {
        this.user.leave();
        localStorage.removeItem('gastric_adci_gun_credentials');
        console.log('Gun.js user logged out');
    },
    
    /**
     * Initialize user-specific features
     */
    initializeUserFeatures() {
        // Setup user's collaborative spaces
        this.setupUserCollaborativeSpaces();
        
        // Setup user's real-time notifications
        this.setupUserNotifications();
        
        // Setup user's shared protocols
        this.setupSharedProtocols();
    },
    
    /**
     * Setup collaborative features
     */
    setupCollaboration() {
        // Real-time decision sharing
        this.setupDecisionSharing();
        
        // Collaborative protocol editing
        this.setupProtocolCollaboration();
        
        // Real-time case discussions
        this.setupCaseDiscussions();
        
        // Evidence sharing
        this.setupEvidenceSharing();
    },
    
    /**
     * Setup real-time decision sharing
     */
    setupDecisionSharing() {
        const decisions = gun.get('gastric_adci_decisions');
        
        // Listen for new decisions
        decisions.map().on((decision, key) => {
            if (decision && decision.shared && this.canAccessDecision(decision)) {
                this.handleSharedDecision(decision, key);
            }
        });
    },
    
    /**
     * Share a decision result
     */
    shareDecision(decisionResult, shareOptions = {}) {
        const decisionData = {
            id: decisionResult.id || Gun.node.uuid(),
            engine: decisionResult.engine_name,
            timestamp: Date.now(),
            confidence: decisionResult.confidence_score,
            recommendation: decisionResult.recommendation,
            sharedBy: this.user.is.pub,
            shareOptions: shareOptions,
            shared: true
        };
        
        // Only include anonymized data for sharing
        if (shareOptions.anonymize) {
            delete decisionData.patientId;
            decisionData.anonymized = true;
        }
        
        const decisions = gun.get('gastric_adci_decisions');
        decisions.get(decisionData.id).put(decisionData);
        
        console.log('Decision shared:', decisionData.id);
        
        // Notify collaborators
        this.notifyCollaborators('decision_shared', {
            decisionId: decisionData.id,
            engine: decisionData.engine
        });
    },
    
    /**
     * Setup collaborative protocol editing
     */
    setupProtocolCollaboration() {
        const protocols = gun.get('gastric_adci_protocols');
        
        // Listen for protocol changes
        protocols.map().on((protocol, key) => {
            if (protocol && this.canAccessProtocol(protocol)) {
                this.handleProtocolUpdate(protocol, key);
            }
        });
    },
    
    /**
     * Start collaborative protocol editing
     */
    startProtocolCollaboration(protocolId, protocolData) {
        const protocols = gun.get('gastric_adci_protocols');
        const protocol = protocols.get(protocolId);
        
        // Initialize collaborative protocol
        protocol.put({
            ...protocolData,
            id: protocolId,
            lastModified: Date.now(),
            lastModifiedBy: this.user.is.pub,
            collaborators: {},
            locked: false
        });
        
        // Setup real-time collaboration
        this.setupProtocolRealtimeEditing(protocolId);
        
        console.log('Protocol collaboration started:', protocolId);
    },
    
    /**
     * Setup real-time protocol editing
     */
    setupProtocolRealtimeEditing(protocolId) {
        const protocol = gun.get('gastric_adci_protocols').get(protocolId);
        
        // Listen for changes
        protocol.get('content').on((content, key) => {
            if (content && key !== 'lastModifiedBy') {
                this.handleProtocolContentChange(protocolId, content, key);
            }
        });
        
        // Track active collaborators
        const collaborators = protocol.get('collaborators');
        collaborators.get(this.user.is.pub).put({
            timestamp: Date.now(),
            active: true
        });
        
        // Listen for other collaborators
        collaborators.map().on((collaborator, userPub) => {
            if (userPub !== this.user.is.pub && collaborator.active) {
                this.handleActiveCollaborator(protocolId, userPub, collaborator);
            }
        });
    },
    
    /**
     * Setup real-time case discussions
     */
    setupCaseDiscussions() {
        const discussions = gun.get('gastric_adci_discussions');
        
        // Listen for new discussion messages
        discussions.map().on((discussion, key) => {
            if (discussion && this.canAccessDiscussion(discussion)) {
                this.handleDiscussionUpdate(discussion, key);
            }
        });
    },
    
    /**
     * Create or join a case discussion
     */
    createCaseDiscussion(caseId, initialMessage) {
        const discussionId = `case_${caseId}_${Date.now()}`;
        const discussions = gun.get('gastric_adci_discussions');
        
        const discussion = {
            id: discussionId,
            caseId: caseId,
            createdBy: this.user.is.pub,
            createdAt: Date.now(),
            participants: {},
            messages: []
        };
        
        discussions.get(discussionId).put(discussion);
        
        // Add initial message
        if (initialMessage) {
            this.addDiscussionMessage(discussionId, initialMessage);
        }
        
        console.log('Case discussion created:', discussionId);
        return discussionId;
    },
    
    /**
     * Add message to discussion
     */
    addDiscussionMessage(discussionId, message) {
        const discussions = gun.get('gastric_adci_discussions');
        const discussion = discussions.get(discussionId);
        
        const messageData = {
            id: Gun.node.uuid(),
            author: this.user.is.pub,
            content: message,
            timestamp: Date.now(),
            type: 'message'
        };
        
        discussion.get('messages').get(messageData.id).put(messageData);
        
        // Update discussion metadata
        discussion.get('lastActivity').put(Date.now());
        discussion.get('participants').get(this.user.is.pub).put({
            lastSeen: Date.now(),
            active: true
        });
        
        console.log('Discussion message added:', messageData.id);
    },
    
    /**
     * Setup evidence sharing
     */
    setupEvidenceSharing() {
        const evidence = gun.get('gastric_adci_evidence');
        
        // Listen for new evidence
        evidence.map().on((evidenceItem, key) => {
            if (evidenceItem && evidenceItem.shared) {
                this.handleSharedEvidence(evidenceItem, key);
            }
        });
    },
    
    /**
     * Share evidence item
     */
    shareEvidence(evidenceData, shareOptions = {}) {
        const evidenceId = evidenceData.id || Gun.node.uuid();
        const evidence = gun.get('gastric_adci_evidence');
        
        const sharedEvidence = {
            ...evidenceData,
            id: evidenceId,
            sharedBy: this.user.is.pub,
            sharedAt: Date.now(),
            shareOptions: shareOptions,
            shared: true
        };
        
        evidence.get(evidenceId).put(sharedEvidence);
        
        console.log('Evidence shared:', evidenceId);
        
        // Notify relevant users
        this.notifyRelevantUsers('evidence_shared', {
            evidenceId: evidenceId,
            type: evidenceData.type,
            indication: evidenceData.indication
        });
    },
    
    /**
     * Setup real-time sync with backend
     */
    setupRealtimeSync() {
        // Sync decisions with backend
        this.syncDecisionsWithBackend();
        
        // Sync protocols with backend
        this.syncProtocolsWithBackend();
        
        // Sync evidence with backend
        this.syncEvidenceWithBackend();
    },
    
    /**
     * Sync decisions with backend
     */
    syncDecisionsWithBackend() {
        const decisions = gun.get('gastric_adci_decisions');
        
        decisions.map().on(async (decision, key) => {
            if (decision && decision.needsBackendSync && this.user.is) {
                try {
                    const response = await fetch('/api/v1/decision-engine/sync', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.GastricADCI.user?.token}`
                        },
                        body: JSON.stringify({
                            gunId: key,
                            decisionData: decision
                        })
                    });
                    
                    if (response.ok) {
                        // Mark as synced
                        decisions.get(key).get('needsBackendSync').put(false);
                        decisions.get(key).get('backendSynced').put(true);
                        decisions.get(key).get('backendSyncTime').put(Date.now());
                    }
                } catch (error) {
                    console.error('Failed to sync decision with backend:', error);
                }
            }
        });
    },
    
    /**
     * Setup offline sync
     */
    setupOfflineSync() {
        // Store Gun.js data locally when offline
        gun.opt({ localStorage: true });
        
        // Listen for online/offline events
        window.addEventListener('online', () => {
            console.log('Gun.js: Online - syncing data');
            this.syncOfflineChanges();
        });
        
        window.addEventListener('offline', () => {
            console.log('Gun.js: Offline - storing changes locally');
        });
    },
    
    /**
     * Sync offline changes when back online
     */
    syncOfflineChanges() {
        // Gun.js handles this automatically, but we can add custom logic
        console.log('Syncing offline changes with Gun.js network');
        
        // Trigger backend sync for important data
        this.syncDecisionsWithBackend();
        this.syncProtocolsWithBackend();
        this.syncEvidenceWithBackend();
    },
    
    /**
     * Setup user notifications
     */
    setupUserNotifications() {
        if (!this.user.is) return;
        
        const notifications = gun.get('gastric_adci_notifications').get(this.user.is.pub);
        
        notifications.map().on((notification, key) => {
            if (notification && !notification.read && notification.timestamp > Date.now() - 86400000) {
                this.handleRealtimeNotification(notification, key);
            }
        });
    },
    
    /**
     * Send notification to user
     */
    sendNotification(userPub, notification) {
        const notifications = gun.get('gastric_adci_notifications').get(userPub);
        
        const notificationData = {
            id: Gun.node.uuid(),
            ...notification,
            from: this.user.is.pub,
            timestamp: Date.now(),
            read: false
        };
        
        notifications.get(notificationData.id).put(notificationData);
        
        console.log('Notification sent to:', userPub);
    },
    
    /**
     * Notify collaborators
     */
    notifyCollaborators(type, data) {
        // Get user's collaborators
        const collaborators = this.getActiveCollaborators();
        
        collaborators.forEach(collaboratorPub => {
            this.sendNotification(collaboratorPub, {
                type: type,
                data: data,
                message: this.getNotificationMessage(type, data)
            });
        });
    },
    
    /**
     * Get active collaborators
     */
    getActiveCollaborators() {
        // This would be implemented based on user's team/groups
        // For now, return empty array
        return [];
    },
    
    /**
     * Permission checks
     */
    canAccessDecision(decision) {
        // Implement access control logic
        return decision.shared || decision.sharedBy === this.user.is.pub;
    },
    
    canAccessProtocol(protocol) {
        // Implement access control logic
        return true; // For now, allow access to all protocols
    },
    
    canAccessDiscussion(discussion) {
        // Implement access control logic
        return discussion.participants && 
               (discussion.participants[this.user.is.pub] || discussion.createdBy === this.user.is.pub);
    },
    
    /**
     * Event handlers
     */
    handleSharedDecision(decision, key) {
        console.log('New shared decision:', decision);
        
        // Show notification in UI
        if (window.GastricADCI.showNotification) {
            window.GastricADCI.showNotification(
                `New decision shared for ${decision.engine} engine`,
                'info'
            );
        }
        
        // Update UI if on relevant page
        if (window.location.pathname.includes('decision')) {
            this.updateDecisionUI(decision);
        }
    },
    
    handleProtocolUpdate(protocol, key) {
        console.log('Protocol updated:', protocol);
        
        // Update UI if viewing this protocol
        if (window.location.pathname.includes(`protocols/${key}`)) {
            this.updateProtocolUI(protocol);
        }
    },
    
    handleDiscussionUpdate(discussion, key) {
        console.log('Discussion updated:', discussion);
        
        // Show notification for new messages
        if (discussion.lastActivity > Date.now() - 10000) { // Within last 10 seconds
            if (window.GastricADCI.showNotification) {
                window.GastricADCI.showNotification(
                    'New message in case discussion',
                    'info'
                );
            }
        }
    },
    
    handleRealtimeNotification(notification, key) {
        console.log('Real-time notification:', notification);
        
        // Show browser notification if permission granted
        if (Notification.permission === 'granted') {
            new Notification('Gastric ADCI Platform', {
                body: notification.message,
                icon: '/static/icons/icon-192x192.png'
            });
        }
        
        // Show in-app notification
        if (window.GastricADCI.showNotification) {
            window.GastricADCI.showNotification(notification.message, 'info');
        }
    },
    
    /**
     * Utility methods
     */
    getNotificationMessage(type, data) {
        const messages = {
            decision_shared: `New decision shared for ${data.engine} engine`,
            protocol_updated: `Protocol updated`,
            evidence_shared: `New evidence shared for ${data.indication}`,
            discussion_message: `New message in case discussion`
        };
        
        return messages[type] || 'New notification';
    },
    
    updateDecisionUI(decision) {
        // Implement UI update logic
        console.log('Updating decision UI:', decision);
    },
    
    updateProtocolUI(protocol) {
        // Implement UI update logic
        console.log('Updating protocol UI:', protocol);
    }
};

// Initialize Gun.js integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.GastricADCI.Gun.init();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.GastricADCI.Gun;
}
