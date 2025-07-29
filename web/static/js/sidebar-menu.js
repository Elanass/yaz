/**
 * Gastric ADCI Platform - Sidebar Menu
 * 
 * This file contains functionality for the sidebar menu system,
 * including opening/closing and category selection.
 */

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
    }
    
    // Category selection
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            categoryItems.forEach(cat => cat.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get the category
            const category = this.getAttribute('data-category');
            
            // You can dispatch a custom event or call a function here
            // to handle category changes
            document.dispatchEvent(new CustomEvent('categoryChanged', {
                detail: { category: category }
            }));
            
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
            if (sidebar.classList.contains('sidebar-open')) {
                closeSidebar();
            }
        }
    });
});
            // Add active class to clicked item
            this.classList.add('active');
            
            // If on mobile, close the sidebar after selection
            if (window.innerWidth < 768) {
                closeSidebar();
            }
            
            // Get the category ID for content switching
            const categoryId = this.getAttribute('data-category');
            
            // In a real app, this would trigger content change
            console.log(`Selected category: ${categoryId}`);
            
            // For demo purposes, show an alert with the selected category
            // In a real app, you would update the main content area
            if (this.querySelector('p')) {
                const categoryName = this.querySelector('p').textContent;
                // Uncomment this for demonstration
                // alert(`Selected category: ${categoryName}`);
            }
        });
    });
});
