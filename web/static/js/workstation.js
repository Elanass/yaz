/**
 * Gastric ADCI Platform - Workstation Functionality
 * 
 * Handles interactions on the workstation page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all case items
    const caseItems = document.querySelectorAll('.case-item');
    
    // Add click event to each case item for easier touch interaction
    caseItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // If the click is not on the arrow link itself, find the link and navigate
            if (!e.target.closest('.case-arrow')) {
                const link = this.querySelector('.case-arrow');
                if (link) {
                    window.location.href = link.getAttribute('href');
                }
            }
        });
    });
    
    // Add case button functionality
    const addCaseButton = document.querySelector('.add-case-button button');
    if (addCaseButton) {
        addCaseButton.addEventListener('click', function() {
            // This would typically open a modal or navigate to a new case form
            // For now, let's just log to console
            console.log('Add new case clicked');
            
            // Redirect to a hypothetical new case form
            window.location.href = '/cases/new';
        });
    }
    
    // Handle back button (if exists)
    const backButton = document.querySelector('[data-action="back"]');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.history.back();
        });
    }
});
