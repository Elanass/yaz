/**
 * Gastric ADCI Platform - Settings Page JavaScript
 * 
 * This file contains functionality specific to the settings page,
 * including theme switching, notification preferences, and user settings.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.querySelector('.has-\\[\\:checked\\]:justify-end input[type="checkbox"]');
    
    // Check local storage for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme based on saved preference or system preference
    if (savedTheme === 'dark' || (savedTheme === null && prefersDark)) {
        document.querySelector('.group\\/design-root').classList.add('dark');
        themeToggle.checked = true;
    } else {
        document.querySelector('.group\\/design-root').classList.remove('dark');
        themeToggle.checked = false;
    }
    
    // Toggle theme when switch is clicked
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.querySelector('.group\\/design-root').classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.querySelector('.group\\/design-root').classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    });
    
    // Back button functionality
    const backButton = document.querySelector('[data-icon="ArrowLeft"]');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.location.href = '/api/v1/';
        });
    }
    
    // Settings option click handlers
    const settingsOptions = document.querySelectorAll('.flex.items-center.gap-4.bg-\\[\\#231810\\]');
    settingsOptions.forEach(option => {
        if (!option.querySelector('label')) { // Skip the toggle switch option
            option.addEventListener('click', function() {
                // In a real app, this would navigate to the specific settings page
                // or open a modal for that setting
                const settingName = option.querySelector('p.text-white.text-base').textContent;
                console.log(`Clicked on ${settingName} settings`);
                
                // For demonstration purposes only - show an alert
                if (settingName !== 'Appearance') {
                    alert(`The ${settingName} settings page is under development.`);
                }
            });
        }
    });
});
