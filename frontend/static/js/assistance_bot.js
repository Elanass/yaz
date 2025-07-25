// Assistance Bot Integration for Gastric ADCI Platform

/**
 * Send a query to the assistance bot API
 * @param {string} question - The clinical question to ask
 * @param {Array} context - Optional context from previous conversation
 * @param {string} specialty - Optional clinical specialty
 * @param {string} userRole - Optional user role for role-specific answers
 * @returns {Promise<Object>} - The bot's response
 */
async function askBot(question, context = [], specialty = null, userRole = null) {
    try {
        const payload = { 
            question,
            context,
            specialty,
            user_role: userRole
        };
        
        const response = await fetch('/api/assistance-bot/bot/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to communicate with the assistance bot:', error);
        throw error;
    }
}

/**
 * Handles a user query to the clinical assistance bot
 * @param {Event} event - The form submit event
 */
async function handleUserQuery(event) {
    if (event) {
        event.preventDefault();
    }
    
    // UI elements
    const questionInput = document.getElementById('user-question');
    const responseElement = document.getElementById('bot-response');
    const sourcesElement = document.getElementById('bot-sources');
    const confidenceElement = document.getElementById('bot-confidence');
    const followUpContainer = document.getElementById('follow-up-suggestions');
    const loadingIndicator = document.getElementById('bot-loading');
    
    if (!questionInput || !responseElement) {
        console.error('Required UI elements not found');
        return;
    }
    
    const question = questionInput.value.trim();
    if (!question) {
        responseElement.textContent = 'Please enter a clinical question.';
        return;
    }
    
    // Get contextual information if available
    const contextElement = document.getElementById('conversation-context');
    const context = contextElement ? JSON.parse(contextElement.value || '[]') : [];
    
    // Get user role if available
    const userRoleElement = document.getElementById('user-role');
    const userRole = userRoleElement ? userRoleElement.value : null;
    
    // Show loading state
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    if (responseElement) {
        responseElement.textContent = 'Processing your clinical query...';
    }
    
    try {
        const response = await askBot(question, context, null, userRole);
        
        // Update the response area
        responseElement.textContent = response.answer;
        
        // Update sources if available
        if (sourcesElement && response.sources) {
            sourcesElement.innerHTML = '';
            response.sources.forEach(source => {
                const sourceItem = document.createElement('li');
                const sourceLink = document.createElement('a');
                sourceLink.href = source.url;
                sourceLink.textContent = source.title;
                sourceLink.target = '_blank';
                sourceItem.appendChild(sourceLink);
                sourcesElement.appendChild(sourceItem);
            });
            
            // Show the sources container
            const sourcesContainer = document.getElementById('sources-container');
            if (sourcesContainer) {
                sourcesContainer.style.display = 'block';
            }
        }
        
        // Update confidence indicator if available
        if (confidenceElement && response.confidence) {
            const confidencePercent = Math.round(response.confidence * 100);
            confidenceElement.textContent = `${confidencePercent}%`;
            
            // Set color based on confidence
            if (confidencePercent >= 90) {
                confidenceElement.className = 'confidence high';
            } else if (confidencePercent >= 75) {
                confidenceElement.className = 'confidence medium';
            } else {
                confidenceElement.className = 'confidence low';
            }
            
            // Show the confidence container
            const confidenceContainer = document.getElementById('confidence-container');
            if (confidenceContainer) {
                confidenceContainer.style.display = 'block';
            }
        }
        
        // Update follow-up suggestions if available
        if (followUpContainer && response.follow_up_suggestions) {
            followUpContainer.innerHTML = '';
            response.follow_up_suggestions.forEach(suggestion => {
                const button = document.createElement('button');
                button.textContent = suggestion;
                button.className = 'follow-up-btn';
                button.addEventListener('click', () => {
                    questionInput.value = suggestion;
                    handleUserQuery();
                });
                followUpContainer.appendChild(button);
            });
            
            followUpContainer.style.display = 'block';
        }
        
        // Add the current question/answer to context for next query
        if (contextElement) {
            const updatedContext = [...context, { 
                question: question, 
                answer: response.answer.substring(0, 100) + '...' // Only store a summary of the answer
            }];
            contextElement.value = JSON.stringify(updatedContext.slice(-5)); // Keep only last 5 exchanges
        }
    } catch (error) {
        responseElement.textContent = 'Unable to get a clinical response at this time. Please try again or contact support.';
        console.error('Bot query failed:', error);
    } finally {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
}

// Initialize the bot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const askButton = document.getElementById('ask-bot-button');
    const questionForm = document.getElementById('bot-question-form');
    
    if (askButton) {
        askButton.addEventListener('click', handleUserQuery);
    }
    
    if (questionForm) {
        questionForm.addEventListener('submit', handleUserQuery);
    }
});
