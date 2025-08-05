/**
 * Discussion Island Component
 * Threaded comments and discussion system for cases
 */

class DiscussionIsland {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            allowReplies: true,
            allowMarkdown: true,
            showVotes: true,
            maxDepth: 3,
            sortOptions: ['newest', 'oldest', 'votes'],
            roles: ['practitioner', 'researcher', 'community'],
            ...options
        };
        this.caseId = options.caseId || null;
        this.discussions = options.discussions || [];
        this.currentUser = options.currentUser || null;
        this.sortBy = 'newest';
        this.replyToId = null;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="discussion-island bg-white rounded-lg shadow-lg p-6" data-component="discussion-island">
                ${this.renderHeader()}
                ${this.renderNewDiscussion()}
                ${this.renderSortControls()}
                ${this.renderDiscussionList()}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
        this.loadDiscussions();
    }

    renderHeader() {
        return `
            <div class="discussion-header flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-gray-900">Case Discussion</h2>
                    <p class="text-gray-600">Share insights and collaborate on case analysis</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="discussion-stats flex items-center space-x-4 text-sm text-gray-600">
                        <span>${this.discussions.length} comments</span>
                        <span>${this.getParticipantCount()} participants</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderNewDiscussion() {
        if (!this.currentUser) {
            return `
                <div class="new-discussion bg-gray-50 rounded-lg p-4 mb-6">
                    <p class="text-gray-600 text-center">Please log in to join the discussion</p>
                </div>
            `;
        }

        return `
            <div class="new-discussion bg-gray-50 rounded-lg p-4 mb-6">
                <div class="flex items-start space-x-4">
                    <div class="user-avatar w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                        ${this.currentUser.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="flex-1">
                        <form class="discussion-form">
                            <div class="mb-3">
                                <textarea 
                                    class="discussion-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                                    rows="3"
                                    placeholder="Share your thoughts on this case..."
                                    maxlength="2000"
                                ></textarea>
                                <div class="text-xs text-gray-500 mt-1">
                                    <span class="char-count">0</span>/2000 characters
                                    ${this.options.allowMarkdown ? '• Markdown supported' : ''}
                                </div>
                            </div>
                            
                            <div class="flex justify-between items-center">
                                <div class="flex items-center space-x-4">
                                    <select class="role-select text-sm border border-gray-300 rounded px-2 py-1">
                                        ${this.options.roles.map(role => `
                                            <option value="${role}" ${this.currentUser.role === role ? 'selected' : ''}>
                                                ${this.formatRoleName(role)}
                                            </option>
                                        `).join('')}
                                    </select>
                                    
                                    ${this.replyToId ? `
                                        <span class="text-sm text-gray-600">
                                            Replying to comment
                                            <button type="button" class="cancel-reply-btn text-blue-600 hover:text-blue-800 ml-1">Cancel</button>
                                        </span>
                                    ` : ''}
                                </div>
                                
                                <div class="flex items-center space-x-2">
                                    <button type="button" class="cancel-btn btn-secondary">Cancel</button>
                                    <button type="submit" class="submit-btn btn-primary">Post Comment</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    renderSortControls() {
        return `
            <div class="sort-controls flex items-center justify-between mb-6">
                <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-700">Sort by:</span>
                    ${this.options.sortOptions.map(option => `
                        <button class="sort-btn px-3 py-1 text-sm rounded-lg transition-colors ${
                            this.sortBy === option 
                                ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                                : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                        }" data-sort="${option}">
                            ${this.formatSortOption(option)}
                        </button>
                    `).join('')}
                </div>
                
                <button class="refresh-discussions-btn btn-secondary">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                    Refresh
                </button>
            </div>
        `;
    }

    renderDiscussionList() {
        const sortedDiscussions = this.sortDiscussions(this.discussions);
        
        if (sortedDiscussions.length === 0) {
            return `
                <div class="discussion-empty text-center py-12">
                    <svg class="mx-auto w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-2.548-.366l-1.905 1.905A1 1 0 018 21.5H3c-.553 0-1-.447-1-1v-5a1 1 0 01.353-.765L4.257 12.9C4.094 11.997 4 11.014 4 10c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
                    </svg>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">No discussions yet</h3>
                    <p class="text-gray-600">Be the first to share your thoughts on this case</p>
                </div>
            `;
        }

        return `
            <div class="discussion-list space-y-6">
                ${sortedDiscussions.map(discussion => this.renderDiscussion(discussion)).join('')}
            </div>
        `;
    }

    renderDiscussion(discussion, depth = 0) {
        const marginClass = depth > 0 ? `ml-${Math.min(depth * 8, 16)}` : '';
        const isAuthor = this.currentUser && discussion.author.id === this.currentUser.id;
        
        return `
            <div class="discussion-item ${marginClass}" data-discussion-id="${discussion.id}">
                <div class="discussion-content bg-white border border-gray-200 rounded-lg p-4">
                    <div class="discussion-header flex items-start justify-between mb-3">
                        <div class="flex items-center space-x-3">
                            <div class="user-avatar w-8 h-8 bg-${this.getRoleColor(discussion.author.role)}-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                                ${discussion.author.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <div class="flex items-center space-x-2">
                                    <span class="font-medium text-gray-900">${discussion.author.name}</span>
                                    <span class="text-xs px-2 py-1 bg-${this.getRoleColor(discussion.author.role)}-100 text-${this.getRoleColor(discussion.author.role)}-800 rounded-full">
                                        ${this.formatRoleName(discussion.author.role)}
                                    </span>
                                </div>
                                <div class="text-sm text-gray-500">
                                    ${this.formatTimestamp(discussion.createdAt)}
                                    ${discussion.editedAt ? '• edited' : ''}
                                </div>
                            </div>
                        </div>
                        
                        <div class="discussion-actions flex items-center space-x-2">
                            ${this.options.showVotes ? `
                                <div class="vote-controls flex items-center space-x-1">
                                    <button class="vote-btn vote-up ${discussion.userVote === 'up' ? 'text-green-600' : 'text-gray-400'}" data-discussion-id="${discussion.id}" data-vote="up">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                                        </svg>
                                    </button>
                                    <span class="vote-count text-sm font-medium">${discussion.votes || 0}</span>
                                    <button class="vote-btn vote-down ${discussion.userVote === 'down' ? 'text-red-600' : 'text-gray-400'}" data-discussion-id="${discussion.id}" data-vote="down">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                                        </svg>
                                    </button>
                                </div>
                            ` : ''}
                            
                            ${isAuthor ? `
                                <button class="edit-discussion-btn text-gray-400 hover:text-gray-600" data-discussion-id="${discussion.id}">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                    </svg>
                                </button>
                                <button class="delete-discussion-btn text-gray-400 hover:text-red-600" data-discussion-id="${discussion.id}">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                    </svg>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="discussion-body">
                        <div class="discussion-text prose prose-sm max-w-none">
                            ${this.renderContent(discussion.content)}
                        </div>
                        
                        ${discussion.attachments && discussion.attachments.length > 0 ? `
                            <div class="discussion-attachments mt-3 flex flex-wrap gap-2">
                                ${discussion.attachments.map(attachment => `
                                    <a href="${attachment.url}" class="attachment-link inline-flex items-center px-2 py-1 bg-gray-100 rounded text-sm text-gray-700 hover:bg-gray-200" target="_blank">
                                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                                        </svg>
                                        ${attachment.name}
                                    </a>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="discussion-footer mt-4 flex items-center justify-between">
                        <div class="discussion-meta flex items-center space-x-4 text-sm text-gray-600">
                            ${discussion.replies && discussion.replies.length > 0 ? `
                                <span>${discussion.replies.length} ${discussion.replies.length === 1 ? 'reply' : 'replies'}</span>
                            ` : ''}
                        </div>
                        
                        <div class="discussion-controls flex items-center space-x-2">
                            ${this.options.allowReplies && depth < this.options.maxDepth ? `
                                <button class="reply-btn text-sm text-blue-600 hover:text-blue-800" data-discussion-id="${discussion.id}">
                                    Reply
                                </button>
                            ` : ''}
                            
                            <button class="share-btn text-sm text-gray-600 hover:text-gray-800" data-discussion-id="${discussion.id}">
                                Share
                            </button>
                        </div>
                    </div>
                </div>
                
                ${discussion.replies && discussion.replies.length > 0 ? `
                    <div class="discussion-replies mt-4 space-y-4">
                        ${discussion.replies.map(reply => this.renderDiscussion(reply, depth + 1)).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderContent(content) {
        if (this.options.allowMarkdown && window.marked) {
            return window.marked.parse(content);
        }
        return content.replace(/\n/g, '<br>');
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Discussion form
        const form = container.querySelector('.discussion-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitDiscussion();
            });

            // Character counter
            const input = form.querySelector('.discussion-input');
            if (input) {
                input.addEventListener('input', (e) => {
                    const charCount = container.querySelector('.char-count');
                    if (charCount) {
                        charCount.textContent = e.target.value.length;
                    }
                });
            }

            // Cancel reply
            const cancelReplyBtn = form.querySelector('.cancel-reply-btn');
            if (cancelReplyBtn) {
                cancelReplyBtn.addEventListener('click', () => {
                    this.cancelReply();
                });
            }
        }

        // Sort controls
        const sortBtns = container.querySelectorAll('.sort-btn');
        sortBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.sortBy = e.target.dataset.sort;
                this.updateSortControls();
                this.updateDiscussionList();
            });
        });

        // Refresh button
        const refreshBtn = container.querySelector('.refresh-discussions-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDiscussions();
            });
        }

        // Vote buttons
        const voteBtns = container.querySelectorAll('.vote-btn');
        voteBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const discussionId = e.currentTarget.dataset.discussionId;
                const vote = e.currentTarget.dataset.vote;
                this.voteOnDiscussion(discussionId, vote);
            });
        });

        // Reply buttons
        const replyBtns = container.querySelectorAll('.reply-btn');
        replyBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const discussionId = e.currentTarget.dataset.discussionId;
                this.replyToDiscussion(discussionId);
            });
        });

        // Edit buttons
        const editBtns = container.querySelectorAll('.edit-discussion-btn');
        editBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const discussionId = e.currentTarget.dataset.discussionId;
                this.editDiscussion(discussionId);
            });
        });

        // Delete buttons
        const deleteBtns = container.querySelectorAll('.delete-discussion-btn');
        deleteBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const discussionId = e.currentTarget.dataset.discussionId;
                this.deleteDiscussion(discussionId);
            });
        });
    }

    async loadDiscussions() {
        if (!this.caseId) return;

        try {
            const response = await fetch(`/api/v1/cases/${this.caseId}/discussions`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                this.discussions = await response.json();
                this.updateDiscussionList();
                this.updateHeader();
            }
        } catch (error) {
            console.error('Error loading discussions:', error);
        }
    }

    async submitDiscussion() {
        const container = document.getElementById(this.containerId);
        const form = container.querySelector('.discussion-form');
        const input = form.querySelector('.discussion-input');
        const roleSelect = form.querySelector('.role-select');
        
        const content = input.value.trim();
        if (!content) return;

        try {
            const response = await fetch('/api/v1/discussions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    caseId: this.caseId,
                    content: content,
                    role: roleSelect.value,
                    parentId: this.replyToId
                })
            });

            if (response.ok) {
                const newDiscussion = await response.json();
                
                if (this.replyToId) {
                    // Add as reply
                    this.addReplyToDiscussion(this.replyToId, newDiscussion);
                    this.cancelReply();
                } else {
                    // Add as new discussion
                    this.discussions.unshift(newDiscussion);
                }

                // Clear form
                input.value = '';
                const charCount = container.querySelector('.char-count');
                if (charCount) {
                    charCount.textContent = '0';
                }

                this.updateDiscussionList();
                this.updateHeader();

                // Dispatch custom event
                container.dispatchEvent(new CustomEvent('discussionAdded', {
                    detail: { discussion: newDiscussion },
                    bubbles: true
                }));
            }
        } catch (error) {
            console.error('Error submitting discussion:', error);
        }
    }

    async voteOnDiscussion(discussionId, vote) {
        try {
            const response = await fetch(`/api/v1/discussions/${discussionId}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({ vote: vote })
            });

            if (response.ok) {
                const result = await response.json();
                this.updateDiscussionVote(discussionId, result);
            }
        } catch (error) {
            console.error('Error voting on discussion:', error);
        }
    }

    replyToDiscussion(discussionId) {
        this.replyToId = discussionId;
        const container = document.getElementById(this.containerId);
        const newDiscussion = container.querySelector('.new-discussion');
        
        if (newDiscussion) {
            newDiscussion.outerHTML = this.renderNewDiscussion();
            this.attachFormEventListeners();
        }

        // Scroll to form
        newDiscussion.scrollIntoView({ behavior: 'smooth' });
    }

    cancelReply() {
        this.replyToId = null;
        const container = document.getElementById(this.containerId);
        const newDiscussion = container.querySelector('.new-discussion');
        
        if (newDiscussion) {
            newDiscussion.outerHTML = this.renderNewDiscussion();
            this.attachFormEventListeners();
        }
    }

    // Helper methods
    sortDiscussions(discussions) {
        const sorted = [...discussions];
        
        switch (this.sortBy) {
            case 'newest':
                return sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            case 'oldest':
                return sorted.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
            case 'votes':
                return sorted.sort((a, b) => (b.votes || 0) - (a.votes || 0));
            default:
                return sorted;
        }
    }

    getParticipantCount() {
        const participants = new Set();
        const countParticipants = (discussions) => {
            discussions.forEach(discussion => {
                participants.add(discussion.author.id);
                if (discussion.replies) {
                    countParticipants(discussion.replies);
                }
            });
        };
        countParticipants(this.discussions);
        return participants.size;
    }

    getRoleColor(role) {
        const colors = {
            'practitioner': 'blue',
            'researcher': 'green',
            'community': 'purple'
        };
        return colors[role] || 'gray';
    }

    formatRoleName(role) {
        const names = {
            'practitioner': 'Practitioner',
            'researcher': 'Researcher',
            'community': 'Community'
        };
        return names[role] || role;
    }

    formatSortOption(option) {
        const options = {
            'newest': 'Newest',
            'oldest': 'Oldest',
            'votes': 'Most Voted'
        };
        return options[option] || option;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) {
            return 'just now';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    updateHeader() {
        const container = document.getElementById(this.containerId);
        const header = container.querySelector('.discussion-header');
        if (header) {
            header.outerHTML = this.renderHeader();
        }
    }

    updateDiscussionList() {
        const container = document.getElementById(this.containerId);
        const list = container.querySelector('.discussion-list');
        if (list) {
            list.outerHTML = this.renderDiscussionList();
            this.attachEventListeners();
        }
    }

    updateSortControls() {
        const container = document.getElementById(this.containerId);
        const controls = container.querySelector('.sort-controls');
        if (controls) {
            controls.outerHTML = this.renderSortControls();
            
            // Reattach sort button listeners
            const sortBtns = container.querySelectorAll('.sort-btn');
            sortBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.sortBy = e.target.dataset.sort;
                    this.updateSortControls();
                    this.updateDiscussionList();
                });
            });
        }
    }

    attachFormEventListeners() {
        const container = document.getElementById(this.containerId);
        const form = container.querySelector('.discussion-form');
        
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitDiscussion();
            });

            const input = form.querySelector('.discussion-input');
            if (input) {
                input.addEventListener('input', (e) => {
                    const charCount = container.querySelector('.char-count');
                    if (charCount) {
                        charCount.textContent = e.target.value.length;
                    }
                });
            }

            const cancelReplyBtn = form.querySelector('.cancel-reply-btn');
            if (cancelReplyBtn) {
                cancelReplyBtn.addEventListener('click', () => {
                    this.cancelReply();
                });
            }
        }
    }

    getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }

    // Public methods
    setCaseId(caseId) {
        this.caseId = caseId;
        this.loadDiscussions();
    }

    addDiscussion(discussion) {
        this.discussions.unshift(discussion);
        this.updateDiscussionList();
        this.updateHeader();
    }

    removeDiscussion(discussionId) {
        this.discussions = this.discussions.filter(d => d.id !== discussionId);
        this.updateDiscussionList();
        this.updateHeader();
    }

    getDiscussions() {
        return this.discussions;
    }
}

// Export for use in other modules
window.DiscussionIsland = DiscussionIsland;
