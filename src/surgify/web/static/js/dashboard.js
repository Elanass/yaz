// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard stats
    loadDashboardStats();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardStats, 30000);
});

async function loadDashboardStats() {
    try {
        const stats = await YAZ.fetch('/api/v1/dashboard/stats');
        
        // Update stat numbers
        const activeCases = YAZ.$('#active-cases');
        const completedToday = YAZ.$('#completed-today');
        
        if (activeCases) activeCases.textContent = stats.activeCases || 0;
        if (completedToday) completedToday.textContent = stats.completedToday || 0;
        
    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
        YAZ.notify('Failed to load dashboard data', 'error');
    }
}
