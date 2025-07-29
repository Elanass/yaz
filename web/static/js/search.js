/**
 * Gastric ADCI Platform - Search Functionality
 * 
 * Handles searching across cases, protocols, and medical terms
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    
    if (!searchInput || !resultsContainer) return;
    
    // Mock data for search results - in a real app, this would come from an API
    const mockData = [
        { type: 'case', id: 'case1', title: 'Patient J.D.', description: 'Stage III Gastric Cancer', date: '2023-06-15' },
        { type: 'case', id: 'case2', title: 'Patient A.S.', description: 'Post-FLOT Assessment', date: '2023-06-10' },
        { type: 'protocol', id: 'prot1', title: 'FLOT Protocol', description: 'Chemotherapy regimen for gastric cancer', date: '2023-05-20' },
        { type: 'protocol', id: 'prot2', title: 'Gastrectomy', description: 'Surgical procedure for gastric cancer', date: '2023-04-30' },
        { type: 'term', id: 'term1', title: 'ADCI', description: 'Adaptive Decision Confidence Index', date: null },
        { type: 'term', id: 'term2', title: 'FLOT', description: 'Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel', date: null }
    ];
    
    // Debounce function to prevent excessive searches while typing
    function debounce(func, timeout = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }
    
    // Search function
    function performSearch(query) {
        if (!query || query.length < 2) {
            resultsContainer.classList.add('hidden');
            return;
        }
        
        // Filter mock data based on query
        const results = mockData.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) || 
            item.description.toLowerCase().includes(query.toLowerCase())
        );
        
        // Display results
        if (results.length > 0) {
            resultsContainer.innerHTML = '';
            resultsContainer.classList.remove('hidden');
            
            results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.className = 'p-3 border-b border-[var(--border-color)] last:border-b-0';
                resultItem.innerHTML = `
                    <div class="flex items-center gap-2">
                        <span class="bg-[var(--bg-accent)] text-[var(--text-on-accent)] px-2 py-0.5 rounded text-xs uppercase">${result.type}</span>
                        <h3 class="font-bold">${result.title}</h3>
                    </div>
                    <p class="text-[var(--text-secondary)] text-sm">${result.description}</p>
                    ${result.date ? `<p class="text-[var(--text-tertiary)] text-xs mt-1">Last updated: ${formatDate(result.date)}</p>` : ''}
                `;
                resultsContainer.appendChild(resultItem);
            });
        } else {
            resultsContainer.innerHTML = '<p class="text-center py-4">No results found</p>';
            resultsContainer.classList.remove('hidden');
        }
    }
    
    // Format date helper
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
    
    // Set up event listener with debounce
    const debouncedSearch = debounce(performSearch);
    searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });
    
    // Clear results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.classList.add('hidden');
        }
    });
});
