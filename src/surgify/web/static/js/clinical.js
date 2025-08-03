// Clinical Workstation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const clinicalApp = YAZ.$('#clinical-app');
    if (!clinicalApp) return;
    
    // Initialize clinical workstation
    initializeClinicalWorkstation();
});

async function initializeClinicalWorkstation() {
    try {
        // Load available cases
        await loadCases();
        
        // Set up case selector
        const caseSelector = YAZ.$('#current-case');
        if (caseSelector) {
            caseSelector.addEventListener('change', handleCaseSelection);
        }
        
    } catch (error) {
        console.error('Failed to initialize clinical workstation:', error);
        YAZ.notify('Failed to load clinical workstation', 'error');
    }
}

async function loadCases() {
    try {
        const cases = await YAZ.fetch('/api/v1/cases');
        const selector = YAZ.$('#current-case');
        
        if (selector && cases) {
            selector.innerHTML = '<option>Select a case...</option>';
            cases.forEach(case_ => {
                const option = document.createElement('option');
                option.value = case_.id;
                option.textContent = `${case_.patientId} - ${case_.procedure}`;
                selector.appendChild(option);
            });
        }
        
    } catch (error) {
        console.error('Failed to load cases:', error);
    }
}

async function handleCaseSelection(event) {
    const caseId = event.target.value;
    if (!caseId || caseId === 'Select a case...') return;
    
    try {
        YAZ.setLoading(event.target, true);
        
        // Load case details
        const caseData = await YAZ.fetch(`/api/v1/cases/${caseId}`);
        const caseDetails = YAZ.$('#case-details');
        
        if (caseDetails && caseData) {
            caseDetails.innerHTML = `
                <h3>Case Details</h3>
                <p><strong>Patient ID:</strong> ${caseData.patientId}</p>
                <p><strong>Procedure:</strong> ${caseData.procedure}</p>
                <p><strong>Status:</strong> ${caseData.status}</p>
            `;
        }
        
        // Load decision support
        await loadDecisionSupport(caseId);
        
    } catch (error) {
        console.error('Failed to load case:', error);
        YAZ.notify('Failed to load case details', 'error');
    } finally {
        YAZ.setLoading(event.target, false);
    }
}

async function loadDecisionSupport(caseId) {
    try {
        const support = await YAZ.fetch(`/api/v1/cases/${caseId}/decision-support`);
        const supportElement = YAZ.$('#decision-support');
        
        if (supportElement && support) {
            supportElement.innerHTML = `
                <h3>Decision Support</h3>
                <div class="recommendations">
                    ${support.recommendations?.map(rec => 
                        `<div class="recommendation">${rec}</div>`
                    ).join('') || 'No recommendations available'}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Failed to load decision support:', error);
    }
}
