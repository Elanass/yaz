/**
 * Surgify Platform - Sidebar Menu
 * 
 * This file contains functionality for the sidebar menu system,
 * including opening/closing and surgical system navigation.
 * Updated to use SharedUtils for DRY compliance.
 */

// Use shared utilities for consistency
const showNotification = UnifiedUtils.notifications.show;

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const menuToggle = document.querySelector('[data-action="toggle-menu"]');
    const closeMenuBtn = document.querySelector('[data-action="close-menu"]');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    const categoryItems = document.querySelectorAll('.category-item');
    
    // Open/close sidebar menu
    function toggleSidebar() {
        if (sidebar.classList.contains('sidebar-open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }
    
    function openSidebar() {
        sidebar.classList.add('sidebar-open');
        sidebar.style.transform = 'translateX(0)';
        sidebarOverlay.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }
    
    function closeSidebar() {
        sidebar.classList.remove('sidebar-open');
        sidebar.style.transform = 'translateX(-100%)';
        sidebarOverlay.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
    
    // Set up event listeners
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleSidebar);
    }
    
    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', closeSidebar);
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    
    // Category selection with navigation
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            categoryItems.forEach(cat => cat.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get the category and URL
            const category = this.getAttribute('data-category');
            const url = this.getAttribute('data-url');
            
            // Navigate to the system page if URL is provided
            if (url) {
                window.location.href = url;
            } else {
                // Fallback: dispatch custom event for dynamic content loading
                document.dispatchEvent(new CustomEvent('systemChanged', {
                    detail: { 
                        system: category,
                        name: this.querySelector('p').textContent
                    }
                }));
                
                // Show feedback to user
                const systemName = this.querySelector('p').textContent;
                console.log(`Navigating to ${systemName} system...`);
                
                // In production, you might want to show a loading state or notification
                // showNotification(`Loading ${systemName} system...`, 'info');
            }
            
            // On mobile, close the sidebar after selection
            if (window.innerWidth < 768) {
                closeSidebar();
            }
        });
    });
    
    // Handle resize events (close sidebar on landscape to portrait changes)
    let lastOrientation = window.orientation;
    window.addEventListener('resize', function() {
        if (lastOrientation !== window.orientation) {
            lastOrientation = window.orientation;
            if (sidebar && sidebar.classList.contains('sidebar-open')) {
                closeSidebar();
            }
        }
    });
    
    // Listen for system change events (for future dynamic content loading)
    document.addEventListener('systemChanged', function(event) {
        const { system, name } = event.detail;
        console.log(`System changed to: ${name} (${system})`);
        
        // Here you could implement dynamic content loading
        // loadSystemContent(system);
    });
});
