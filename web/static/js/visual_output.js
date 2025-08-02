/**
 * Visual Output Enhancements for Gastric ADCI Platform
 */

// Enhanced visual feedback for user interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons
    document.querySelectorAll('button, .btn').forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.style.opacity = '0.7';
                setTimeout(() => {
                    this.style.opacity = '1';
                }, 150);
            }
        });
    });
    
    // Smooth animations for cards and panels
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    document.querySelectorAll('.case-item, .card, .panel').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        observer.observe(el);
    });
});
