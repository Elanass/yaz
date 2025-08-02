/**
 * Gastric ADCI Platform - Add Case Functionality
 * 
 * Handles interactions on the add case page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle form validation
    const caseTitle = document.getElementById('case-title');
    const specialty = document.getElementById('surgical-specialty');
    const procedureDetails = document.getElementById('procedure-details');
    const procedureDate = document.getElementById('procedure-date');
    const saveButton = document.querySelector('.save-button');
    
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            // Basic validation
            let isValid = true;
            
            // Required fields validation
            if (!caseTitle.value.trim()) {
                highlightInvalid(caseTitle);
                isValid = false;
            } else {
                resetValidation(caseTitle);
            }
            
            if (!specialty.value) {
                highlightInvalid(specialty);
                isValid = false;
            } else {
                resetValidation(specialty);
            }
            
            if (!procedureDetails.value.trim()) {
                highlightInvalid(procedureDetails);
                isValid = false;
            } else {
                resetValidation(procedureDetails);
            }
            
            if (!procedureDate.value) {
                highlightInvalid(procedureDate);
                isValid = false;
            } else {
                resetValidation(procedureDate);
            }
            
            if (isValid) {
                // Form is valid, submit data
                submitCaseData();
            }
        });
    }
    
    // Handle file uploads
    const uploadButton = document.querySelector('.upload-button');
    if (uploadButton) {
        uploadButton.addEventListener('click', function() {
            // Create a file input element
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*,video/*';
            fileInput.multiple = true;
            
            // Trigger the file dialog
            fileInput.click();
            
            // Handle file selection
            fileInput.addEventListener('change', function() {
                if (fileInput.files.length > 0) {
                    console.log(`${fileInput.files.length} files selected`);
                    // Here you would typically upload the files or prepare them for submission
                    // For now, we'll just show a message in the upload container
                    const uploadContainer = document.querySelector('.upload-container');
                    
                    // Create file preview elements
                    const preview = document.createElement('div');
                    preview.className = 'file-preview';
                    preview.innerHTML = `<p>${fileInput.files.length} file(s) selected for upload</p>`;
                    
                    // Replace upload content with preview
                    uploadContainer.innerHTML = '';
                    uploadContainer.appendChild(preview);
                    
                    // Add back the upload button
                    const newUploadButton = document.createElement('button');
                    newUploadButton.className = 'upload-button';
                    newUploadButton.innerHTML = '<span>Change Files</span>';
                    uploadContainer.appendChild(newUploadButton);
                    
                    // Reattach the event listener to the new button
                    newUploadButton.addEventListener('click', function() {
                        fileInput.click();
                    });
                }
            });
        });
    }
    
    // Back button functionality
    const backButton = document.querySelector('[data-icon="X"]');
    if (backButton) {
        backButton.addEventListener('click', function() {
            // Go back to previous page
            window.history.back();
        });
    }
    
    // Helper functions - using shared utilities
    function highlightInvalid(element) {
        UnifiedUtils.ValidationRules.highlightInvalid(element);
    }
    
    function resetValidation(element) {
        UnifiedUtils.ValidationRules.resetValidation(element);
    }
    
    function submitCaseData() {
        // Create payload from form fields
        const payload = {
            title: caseTitle.value.trim(),
            specialty: specialty.value,
            patientId: document.getElementById('patient-id').value.trim(),
            procedureDetails: procedureDetails.value.trim(),
            date: procedureDate.value,
            location: document.getElementById('location').value.trim()
            // Files would be handled separately via FormData in a real implementation
        };
        
        // Show loading state on button
        saveButton.innerHTML = '<span>Saving...</span>';
        saveButton.disabled = true;
        
        console.log('Submitting case data:', payload);
        
        // Simulate API call
        setTimeout(function() {
            // In a real implementation, this would be an actual API call
            // For now, we'll just redirect to the workstation page
            window.location.href = '/workstation';
        }, 1500);
    }
});
