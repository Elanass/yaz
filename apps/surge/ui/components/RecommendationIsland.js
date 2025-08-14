/**
 * Recommendation Island Component
 * AI-powered recommendations and decision support with feedback loops
 */

class RecommendationIsland {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            showFeedback: true,
            allowRating: true,
            showConfidence: true,
            roles: ['practitioner', 'researcher', 'community'],
            categories: ['diagnosis', 'treatment', 'procedure', 'followup'],
            ...options
        };
        this.caseId = options.caseId || null;
        this.recommendations = options.recommendations || [];
        this.currentUser = options.currentUser || null;
        this.selectedCategory = 'all';
        this.feedbackData = {};
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="recommendation-island bg-white rounded-lg shadow-lg p-6" data-component="recommendation-island">
                ${this.renderHeader()}
                ${this.renderFilters()}
                ${this.renderRecommendationList()}
                ${this.renderFeedbackSummary()}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
        this.loadRecommendations();
    }

    renderHeader() {
        return `
            <div class="recommendation-header flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-gray-900">AI Recommendations</h2>
                    <p class="text-gray-600">Evidence-based decision support with community feedback</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="recommendation-stats flex items-center space-x-4 text-sm text-gray-600">
                        <span>${this.recommendations.length} recommendations</span>
                        <span>${this.getFeedbackCount()} reviews</span>
                    </div>
                    <button class="refresh-recommendations-btn btn-secondary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        Refresh
                    </button>
                </div>
            </div>
        `;
    }

    renderFilters() {
        return `
            <div class="recommendation-filters mb-6">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="text-sm font-medium text-gray-700">Filter by category:</span>
                    <button class="category-filter-btn px-3 py-1 text-sm rounded-lg transition-colors ${
                        this.selectedCategory === 'all' 
                            ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                            : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                    }" data-category="all">
                        All
                    </button>
                    ${this.options.categories.map(category => `
                        <button class="category-filter-btn px-3 py-1 text-sm rounded-lg transition-colors ${
                            this.selectedCategory === category 
                                ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                                : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                        }" data-category="${category}">
                            ${this.formatCategoryName(category)}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderRecommendationList() {
        const filteredRecommendations = this.filterRecommendations(this.recommendations);
        
        if (filteredRecommendations.length === 0) {
            return `
                <div class="recommendation-empty text-center py-12">
                    <svg class="mx-auto w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">No recommendations available</h3>
                    <p class="text-gray-600">AI recommendations will appear here based on case analysis</p>
                </div>
            `;
        }

        return `
            <div class="recommendation-list space-y-6">
                ${filteredRecommendations.map(recommendation => this.renderRecommendation(recommendation)).join('')}
            </div>
        `;
    }

    renderRecommendation(recommendation) {
        const avgRating = this.calculateAverageRating(recommendation.id);
        const userRating = this.getUserRating(recommendation.id);
        const feedbackCount = this.getFeedbackCountForRecommendation(recommendation.id);

        return `
            <div class="recommendation-item border border-gray-200 rounded-lg p-6" data-recommendation-id="${recommendation.id}">
                <div class="recommendation-header flex items-start justify-between mb-4">
                    <div class="flex-1">
                        <div class="flex items-center space-x-3 mb-2">
                            <span class="category-badge px-2 py-1 text-xs font-medium bg-${this.getCategoryColor(recommendation.category)}-100 text-${this.getCategoryColor(recommendation.category)}-800 rounded-full">
                                ${this.formatCategoryName(recommendation.category)}
                            </span>
                            ${this.options.showConfidence ? `
                                <div class="confidence-indicator flex items-center space-x-1">
                                    <span class="text-sm text-gray-600">Confidence:</span>
                                    <div class="confidence-bar w-16 h-2 bg-gray-200 rounded-full">
                                        <div class="bg-${this.getConfidenceColor(recommendation.confidence)}-500 h-2 rounded-full" style="width: ${recommendation.confidence}%"></div>
                                    </div>
                                    <span class="text-sm font-medium text-gray-700">${recommendation.confidence}%</span>
                                </div>
                            ` : ''}
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">${recommendation.title}</h3>
                    </div>
                    
                    <div class="recommendation-actions flex items-center space-x-2">
                        <button class="bookmark-btn ${recommendation.isBookmarked ? 'text-yellow-500' : 'text-gray-400'} hover:text-yellow-500" data-recommendation-id="${recommendation.id}" title="Bookmark">
                            <svg class="w-5 h-5" fill="${recommendation.isBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path>
                            </svg>
                        </button>
                        <button class="share-btn text-gray-400 hover:text-gray-600" data-recommendation-id="${recommendation.id}" title="Share">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="recommendation-content mb-4">
                    <p class="text-gray-700 mb-3">${recommendation.description}</p>
                    
                    ${recommendation.evidence && recommendation.evidence.length > 0 ? `
                        <div class="evidence-section">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">Supporting Evidence:</h4>
                            <ul class="space-y-1">
                                ${recommendation.evidence.map(evidence => `
                                    <li class="text-sm text-gray-600 flex items-start">
                                        <span class="w-1 h-1 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                        <span>${evidence.description} 
                                            ${evidence.source ? `<a href="${evidence.source}" class="text-blue-600 hover:text-blue-800" target="_blank">(Source)</a>` : ''}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${recommendation.steps && recommendation.steps.length > 0 ? `
                        <div class="steps-section mt-4">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">Recommended Steps:</h4>
                            <ol class="space-y-2">
                                ${recommendation.steps.map((step, index) => `
                                    <li class="text-sm text-gray-700 flex items-start">
                                        <span class="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-800 text-xs font-medium rounded-full flex items-center justify-center mr-3 mt-0.5">
                                            ${index + 1}
                                        </span>
                                        ${step}
                                    </li>
                                `).join('')}
                            </ol>
                        </div>
                    ` : ''}
                </div>
                
                ${this.options.showFeedback ? `
                    <div class="recommendation-feedback border-t border-gray-200 pt-4">
                        <div class="flex items-center justify-between mb-4">
                            <div class="feedback-stats flex items-center space-x-4">
                                ${this.options.allowRating ? `
                                    <div class="rating-display flex items-center space-x-2">
                                        <div class="stars flex items-center">
                                            ${this.renderStars(avgRating)}
                                        </div>
                                        <span class="text-sm text-gray-600">${avgRating.toFixed(1)} (${feedbackCount} reviews)</span>
                                    </div>
                                ` : ''}
                            </div>
                            
                            <button class="show-feedback-btn text-sm text-blue-600 hover:text-blue-800" data-recommendation-id="${recommendation.id}">
                                ${feedbackCount > 0 ? `View ${feedbackCount} reviews` : 'Be the first to review'}
                            </button>
                        </div>
                        
                        ${this.currentUser ? `
                            <div class="user-rating mb-4">
                                <div class="flex items-center space-x-3">
                                    <span class="text-sm font-medium text-gray-700">Your rating:</span>
                                    <div class="rating-input flex items-center space-x-1" data-recommendation-id="${recommendation.id}">
                                        ${[1, 2, 3, 4, 5].map(star => `
                                            <button class="star-btn ${star <= userRating ? 'text-yellow-500' : 'text-gray-300'} hover:text-yellow-500" data-star="${star}">
                                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                                                </svg>
                                            </button>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="feedback-form ${userRating > 0 ? '' : 'hidden'}">
                                <textarea 
                                    class="feedback-input w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                                    rows="2"
                                    placeholder="Share your experience with this recommendation..."
                                    data-recommendation-id="${recommendation.id}"
                                >${this.getUserFeedback(recommendation.id)}</textarea>
                                <div class="flex justify-between items-center mt-2">
                                    <div class="flex items-center space-x-2">
                                        <select class="role-select text-xs border border-gray-300 rounded px-2 py-1" data-recommendation-id="${recommendation.id}">
                                            ${this.options.roles.map(role => `
                                                <option value="${role}" ${this.currentUser.role === role ? 'selected' : ''}>
                                                    ${this.formatRoleName(role)}
                                                </option>
                                            `).join('')}
                                        </select>
                                    </div>
                                    <button class="submit-feedback-btn btn-sm btn-primary" data-recommendation-id="${recommendation.id}">
                                        Submit Feedback
                                    </button>
                                </div>
                            </div>
                        ` : `
                            <div class="login-prompt text-center py-4">
                                <p class="text-sm text-gray-600">Please log in to rate and provide feedback</p>
                            </div>
                        `}
                        
                        <div class="feedback-list hidden" data-recommendation-id="${recommendation.id}">
                            <!-- Feedback items will be loaded here -->
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let starsHtml = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHtml += `
                <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                </svg>
            `;
        }
        
        // Half star
        if (hasHalfStar) {
            starsHtml += `
                <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <defs>
                        <linearGradient id="half-star">
                            <stop offset="50%" stop-color="currentColor"/>
                            <stop offset="50%" stop-color="#d1d5db"/>
                        </linearGradient>
                    </defs>
                    <path fill="url(#half-star)" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                </svg>
            `;
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += `
                <svg class="w-4 h-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                </svg>
            `;
        }
        
        return starsHtml;
    }

    renderFeedbackSummary() {
        const totalFeedback = this.getTotalFeedbackCount();
        if (totalFeedback === 0) return '';

        const roleSummary = this.getFeedbackByRole();
        const avgRatingOverall = this.getOverallAverageRating();

        return `
            <div class="feedback-summary bg-gray-50 rounded-lg p-6 mt-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Community Feedback Summary</h3>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="overall-rating text-center">
                        <div class="text-3xl font-bold text-blue-600 mb-1">${avgRatingOverall.toFixed(1)}</div>
                        <div class="stars flex justify-center mb-2">
                            ${this.renderStars(avgRatingOverall)}
                        </div>
                        <div class="text-sm text-gray-600">${totalFeedback} total reviews</div>
                    </div>
                    
                    <div class="role-breakdown">
                        <h4 class="text-sm font-semibold text-gray-900 mb-3">By Role</h4>
                        <div class="space-y-2">
                            ${Object.entries(roleSummary).map(([role, data]) => `
                                <div class="flex justify-between items-center text-sm">
                                    <span class="text-gray-700">${this.formatRoleName(role)}</span>
                                    <div class="flex items-center space-x-2">
                                        <div class="stars flex">
                                            ${this.renderStars(data.avgRating)}
                                        </div>
                                        <span class="text-gray-600">(${data.count})</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="top-feedback">
                        <h4 class="text-sm font-semibold text-gray-900 mb-3">Top Feedback</h4>
                        <div class="space-y-2">
                            ${this.getTopFeedback().map(feedback => `
                                <div class="text-xs text-gray-600 bg-white rounded p-2">
                                    <div class="flex items-center space-x-1 mb-1">
                                        ${this.renderStars(feedback.rating)}
                                        <span class="text-${this.getRoleColor(feedback.role)}-600 font-medium">
                                            ${this.formatRoleName(feedback.role)}
                                        </span>
                                    </div>
                                    <p class="text-gray-700">${feedback.comment.substring(0, 60)}${feedback.comment.length > 60 ? '...' : ''}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Category filters
        const categoryBtns = container.querySelectorAll('.category-filter-btn');
        categoryBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectedCategory = e.target.dataset.category;
                this.updateFilters();
                this.updateRecommendationList();
            });
        });

        // Refresh button
        const refreshBtn = container.querySelector('.refresh-recommendations-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadRecommendations();
            });
        }

        // Star rating inputs
        const starBtns = container.querySelectorAll('.star-btn');
        starBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const recommendationId = e.target.closest('.rating-input').dataset.recommendationId;
                const rating = parseInt(e.target.dataset.star);
                this.setUserRating(recommendationId, rating);
            });
        });

        // Feedback submission
        const submitBtns = container.querySelectorAll('.submit-feedback-btn');
        submitBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const recommendationId = e.target.dataset.recommendationId;
                this.submitFeedback(recommendationId);
            });
        });

        // Show feedback toggle
        const showFeedbackBtns = container.querySelectorAll('.show-feedback-btn');
        showFeedbackBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const recommendationId = e.target.dataset.recommendationId;
                this.toggleFeedbackList(recommendationId);
            });
        });

        // Bookmark buttons
        const bookmarkBtns = container.querySelectorAll('.bookmark-btn');
        bookmarkBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const recommendationId = e.target.dataset.recommendationId;
                this.toggleBookmark(recommendationId);
            });
        });
    }

    async loadRecommendations() {
        if (!this.caseId) return;

        try {
            const response = await fetch(`/api/v1/cases/${this.caseId}/recommendations`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                this.recommendations = await response.json();
                this.updateRecommendationList();
                this.updateHeader();
                await this.loadFeedbackData();
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    async loadFeedbackData() {
        try {
            const response = await fetch(`/api/v1/cases/${this.caseId}/recommendations/feedback`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                this.feedbackData = await response.json();
                this.updateRecommendationList();
            }
        } catch (error) {
            console.error('Error loading feedback data:', error);
        }
    }

    async setUserRating(recommendationId, rating) {
        const container = document.getElementById(this.containerId);
        const ratingInput = container.querySelector(`[data-recommendation-id="${recommendationId}"] .rating-input`);
        const feedbackForm = container.querySelector(`[data-recommendation-id="${recommendationId}"] .feedback-form`);

        // Update UI immediately
        const starBtns = ratingInput.querySelectorAll('.star-btn');
        starBtns.forEach((btn, index) => {
            if (index < rating) {
                btn.classList.remove('text-gray-300');
                btn.classList.add('text-yellow-500');
            } else {
                btn.classList.remove('text-yellow-500');
                btn.classList.add('text-gray-300');
            }
        });

        // Show feedback form
        if (feedbackForm) {
            feedbackForm.classList.remove('hidden');
        }

        try {
            const response = await fetch(`/api/v1/recommendations/${recommendationId}/rating`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({ rating: rating })
            });

            if (!response.ok) {
                // Revert UI on error
                this.updateRecommendationList();
            }
        } catch (error) {
            console.error('Error setting rating:', error);
            this.updateRecommendationList();
        }
    }

    async submitFeedback(recommendationId) {
        const container = document.getElementById(this.containerId);
        const feedbackInput = container.querySelector(`[data-recommendation-id="${recommendationId}"] .feedback-input`);
        const roleSelect = container.querySelector(`[data-recommendation-id="${recommendationId}"] .role-select`);
        
        const feedback = feedbackInput.value.trim();
        if (!feedback) return;

        try {
            const response = await fetch(`/api/v1/recommendations/${recommendationId}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    comment: feedback,
                    role: roleSelect.value
                })
            });

            if (response.ok) {
                // Clear form
                feedbackInput.value = '';
                
                // Reload feedback data
                await this.loadFeedbackData();
                
                // Show success message
                this.showFeedbackSuccess(recommendationId);
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    }

    async toggleBookmark(recommendationId) {
        try {
            const response = await fetch(`/api/v1/recommendations/${recommendationId}/bookmark`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.updateBookmarkUI(recommendationId, result.isBookmarked);
            }
        } catch (error) {
            console.error('Error toggling bookmark:', error);
        }
    }

    filterRecommendations(recommendations) {
        if (this.selectedCategory === 'all') {
            return recommendations;
        }
        return recommendations.filter(rec => rec.category === this.selectedCategory);
    }

    // Helper methods
    formatCategoryName(category) {
        const names = {
            'diagnosis': 'Diagnosis',
            'treatment': 'Treatment',
            'procedure': 'Procedure',
            'followup': 'Follow-up'
        };
        return names[category] || category;
    }

    formatRoleName(role) {
        const names = {
            'practitioner': 'Practitioner',
            'researcher': 'Researcher', 
            'community': 'Community'
        };
        return names[role] || role;
    }

    getCategoryColor(category) {
        const colors = {
            'diagnosis': 'blue',
            'treatment': 'green',
            'procedure': 'purple',
            'followup': 'orange'
        };
        return colors[category] || 'gray';
    }

    getRoleColor(role) {
        const colors = {
            'practitioner': 'blue',
            'researcher': 'green',
            'community': 'purple'
        };
        return colors[role] || 'gray';
    }

    getConfidenceColor(confidence) {
        if (confidence >= 80) return 'green';
        if (confidence >= 60) return 'yellow';
        return 'red';
    }

    calculateAverageRating(recommendationId) {
        const feedback = this.feedbackData[recommendationId] || [];
        if (feedback.length === 0) return 0;
        
        const sum = feedback.reduce((total, item) => total + item.rating, 0);
        return sum / feedback.length;
    }

    getUserRating(recommendationId) {
        const feedback = this.feedbackData[recommendationId] || [];
        const userFeedback = feedback.find(f => f.userId === this.currentUser?.id);
        return userFeedback ? userFeedback.rating : 0;
    }

    getUserFeedback(recommendationId) {
        const feedback = this.feedbackData[recommendationId] || [];
        const userFeedback = feedback.find(f => f.userId === this.currentUser?.id);
        return userFeedback ? userFeedback.comment : '';
    }

    getFeedbackCount() {
        return Object.values(this.feedbackData).reduce((total, feedback) => total + feedback.length, 0);
    }

    getFeedbackCountForRecommendation(recommendationId) {
        return (this.feedbackData[recommendationId] || []).length;
    }

    getTotalFeedbackCount() {
        return Object.values(this.feedbackData).reduce((total, feedback) => total + feedback.length, 0);
    }

    getFeedbackByRole() {
        const roleSummary = {};
        
        Object.values(this.feedbackData).forEach(feedbackList => {
            feedbackList.forEach(feedback => {
                if (!roleSummary[feedback.role]) {
                    roleSummary[feedback.role] = { count: 0, totalRating: 0, avgRating: 0 };
                }
                roleSummary[feedback.role].count++;
                roleSummary[feedback.role].totalRating += feedback.rating;
                roleSummary[feedback.role].avgRating = roleSummary[feedback.role].totalRating / roleSummary[feedback.role].count;
            });
        });
        
        return roleSummary;
    }

    getOverallAverageRating() {
        let totalRating = 0;
        let totalCount = 0;
        
        Object.values(this.feedbackData).forEach(feedbackList => {
            feedbackList.forEach(feedback => {
                totalRating += feedback.rating;
                totalCount++;
            });
        });
        
        return totalCount > 0 ? totalRating / totalCount : 0;
    }

    getTopFeedback() {
        const allFeedback = [];
        
        Object.values(this.feedbackData).forEach(feedbackList => {
            allFeedback.push(...feedbackList.filter(f => f.comment && f.comment.length > 20));
        });
        
        return allFeedback
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 3);
    }

    updateHeader() {
        const container = document.getElementById(this.containerId);
        const header = container.querySelector('.recommendation-header');
        if (header) {
            header.outerHTML = this.renderHeader();
        }
    }

    updateFilters() {
        const container = document.getElementById(this.containerId);
        const filters = container.querySelector('.recommendation-filters');
        if (filters) {
            filters.outerHTML = this.renderFilters();
            
            // Reattach event listeners
            const categoryBtns = container.querySelectorAll('.category-filter-btn');
            categoryBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.selectedCategory = e.target.dataset.category;
                    this.updateFilters();
                    this.updateRecommendationList();
                });
            });
        }
    }

    updateRecommendationList() {
        const container = document.getElementById(this.containerId);
        const list = container.querySelector('.recommendation-list');
        if (list) {
            list.outerHTML = this.renderRecommendationList();
            this.attachEventListeners();
        }
    }

    updateBookmarkUI(recommendationId, isBookmarked) {
        const container = document.getElementById(this.containerId);
        const bookmarkBtn = container.querySelector(`[data-recommendation-id="${recommendationId}"] .bookmark-btn`);
        
        if (bookmarkBtn) {
            if (isBookmarked) {
                bookmarkBtn.classList.remove('text-gray-400');
                bookmarkBtn.classList.add('text-yellow-500');
                bookmarkBtn.querySelector('svg').setAttribute('fill', 'currentColor');
            } else {
                bookmarkBtn.classList.remove('text-yellow-500');
                bookmarkBtn.classList.add('text-gray-400');
                bookmarkBtn.querySelector('svg').setAttribute('fill', 'none');
            }
        }
    }

    showFeedbackSuccess(recommendationId) {
        const container = document.getElementById(this.containerId);
        const item = container.querySelector(`[data-recommendation-id="${recommendationId}"]`);
        
        // Show temporary success message
        const successMsg = document.createElement('div');
        successMsg.className = 'feedback-success bg-green-100 text-green-800 text-sm p-2 rounded mt-2';
        successMsg.textContent = 'Thank you for your feedback!';
        
        const feedbackSection = item.querySelector('.recommendation-feedback');
        feedbackSection.appendChild(successMsg);
        
        setTimeout(() => {
            successMsg.remove();
        }, 3000);
    }

    getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }

    // Public methods
    setCaseId(caseId) {
        this.caseId = caseId;
        this.loadRecommendations();
    }

    addRecommendation(recommendation) {
        this.recommendations.unshift(recommendation);
        this.updateRecommendationList();
        this.updateHeader();
    }

    removeRecommendation(recommendationId) {
        this.recommendations = this.recommendations.filter(r => r.id !== recommendationId);
        this.updateRecommendationList();
        this.updateHeader();
    }

    getRecommendations() {
        return this.recommendations;
    }

    getFeedbackSummary() {
        return {
            totalCount: this.getTotalFeedbackCount(),
            averageRating: this.getOverallAverageRating(),
            byRole: this.getFeedbackByRole()
        };
    }
}

// Export for use in other modules
window.RecommendationIsland = RecommendationIsland;
