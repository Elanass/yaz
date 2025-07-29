/**
 * Gastric ADCI Platform - Theme Switcher
 * 
 * This file contains functionality for switching between light and dark themes
 * across the entire application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme based on saved preference or system preference
    if (savedTheme === 'dark' || (savedTheme === null && prefersDark)) {
        document.documentElement.classList.add('dark-mode');
        document.querySelector('.group\\/design-root')?.classList.add('dark');
        
        // Set any theme toggles to checked state
        document.querySelectorAll('.theme-toggle').forEach(toggle => {
            if (toggle.type === 'checkbox') {
                toggle.checked = true;
            }
        });
    } else {
        document.documentElement.classList.remove('dark-mode');
        document.querySelector('.group\\/design-root')?.classList.remove('dark');
        
        // Set any theme toggles to unchecked state
        document.querySelectorAll('.theme-toggle').forEach(toggle => {
            if (toggle.type === 'checkbox') {
                toggle.checked = false;
            }
        });
    }
    
    // Set up event listeners for theme toggle buttons/switches
    document.querySelectorAll('.theme-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.classList.add('dark-mode');
                document.querySelector('.group\\/design-root')?.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark-mode');
                document.querySelector('.group\\/design-root')?.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
        });
    });
});
