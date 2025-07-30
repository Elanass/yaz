"""
Education dashboard components for YAZ Surgery Analytics Platform.
Provides UI components for medical education and training management.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

def render_education_dashboard(user_data: Dict[str, Any]) -> str:
    """Render main education dashboard."""
    return f"""
    <div class="education-dashboard">
        <div class="dashboard-header">
            <h2>Medical Education & Training</h2>
            <div class="user-info">
                <span>Welcome, Dr. {user_data.get('name', 'User')}</span>
                <span class="role-badge">{user_data.get('role', 'Healthcare Professional')}</span>
            </div>
        </div>
        
        <div class="dashboard-grid">
            {render_training_progress_card()}
            {render_certification_status_card()}
            {render_recommended_courses_card()}
            {render_continuing_education_card()}
        </div>
        
        <div class="dashboard-sections">
            {render_active_programs_section()}
            {render_surgery_outcome_integration_section()}
            {render_professional_development_section()}
        </div>
    </div>
    """

def render_training_progress_card() -> str:
    """Render training progress overview card."""
    return """
    <div class="dashboard-card training-progress">
        <div class="card-header">
            <h3>Training Progress</h3>
            <div class="progress-indicator">
                <div class="progress-circle" data-progress="75">
                    <span class="progress-text">75%</span>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div class="skill-metrics">
                <div class="skill-item">
                    <span class="skill-name">Laparoscopic Techniques</span>
                    <div class="skill-bar">
                        <div class="skill-progress" style="width: 85%"></div>
                    </div>
                </div>
                <div class="skill-item">
                    <span class="skill-name">Patient Consultation</span>
                    <div class="skill-bar">
                        <div class="skill-progress" style="width: 92%"></div>
                    </div>
                </div>
                <div class="skill-item">
                    <span class="skill-name">Robotic Surgery</span>
                    <div class="skill-bar">
                        <div class="skill-progress" style="width: 68%"></div>
                    </div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="viewDetailedProgress()">View Details</button>
                <button class="btn btn-secondary" onclick="scheduleTraining()">Schedule Training</button>
            </div>
        </div>
    </div>
    """

def render_certification_status_card() -> str:
    """Render certification status card."""
    return """
    <div class="dashboard-card certification-status">
        <div class="card-header">
            <h3>Certifications</h3>
            <span class="status-badge status-current">Current</span>
        </div>
        <div class="card-body">
            <div class="certification-list">
                <div class="cert-item">
                    <div class="cert-info">
                        <span class="cert-name">Board Certification - General Surgery</span>
                        <span class="cert-expiry">Expires: Dec 2025</span>
                    </div>
                    <span class="cert-status valid">Valid</span>
                </div>
                <div class="cert-item">
                    <div class="cert-info">
                        <span class="cert-name">Laparoscopic Surgery Certificate</span>
                        <span class="cert-expiry">Expires: Mar 2024</span>
                    </div>
                    <span class="cert-status warning">Renewal Due</span>
                </div>
                <div class="cert-item">
                    <div class="cert-info">
                        <span class="cert-name">CME Credits</span>
                        <span class="cert-expiry">Required: 50 credits/year</span>
                    </div>
                    <span class="cert-status progress">32/50</span>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="manageCertifications()">Manage</button>
                <button class="btn btn-secondary" onclick="renewCertification()">Renew</button>
            </div>
        </div>
    </div>
    """

def render_recommended_courses_card() -> str:
    """Render recommended courses card."""
    return """
    <div class="dashboard-card recommended-courses">
        <div class="card-header">
            <h3>Recommended Courses</h3>
            <span class="recommendation-count">5 New</span>
        </div>
        <div class="card-body">
            <div class="course-list">
                <div class="course-item">
                    <div class="course-info">
                        <h4>Advanced Bariatric Surgery Techniques</h4>
                        <p>Mayo Clinic - 16 hours CME</p>
                        <div class="course-meta">
                            <span class="course-level">Advanced</span>
                            <span class="course-format">Online + Hands-on</span>
                        </div>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-sm btn-primary">Enroll</button>
                        <button class="btn btn-sm btn-outline">Learn More</button>
                    </div>
                </div>
                <div class="course-item">
                    <div class="course-info">
                        <h4>Patient Safety in Minimally Invasive Surgery</h4>
                        <p>Johns Hopkins - 8 hours CME</p>
                        <div class="course-meta">
                            <span class="course-level">Intermediate</span>
                            <span class="course-format">Virtual</span>
                        </div>
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-sm btn-primary">Enroll</button>
                        <button class="btn btn-sm btn-outline">Learn More</button>
                    </div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="viewAllCourses()">View All Courses</button>
            </div>
        </div>
    </div>
    """

def render_continuing_education_card() -> str:
    """Render continuing education requirements card."""
    return """
    <div class="dashboard-card continuing-education">
        <div class="card-header">
            <h3>Continuing Education</h3>
            <div class="compliance-indicator">
                <span class="compliance-status on-track">On Track</span>
            </div>
        </div>
        <div class="card-body">
            <div class="ce-requirements">
                <div class="requirement-item">
                    <span class="req-name">Annual CME Credits</span>
                    <div class="req-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 64%"></div>
                        </div>
                        <span class="progress-text">32/50</span>
                    </div>
                </div>
                <div class="requirement-item">
                    <span class="req-name">Patient Safety Training</span>
                    <div class="req-progress">
                        <div class="progress-bar">
                            <div class="progress-fill complete" style="width: 100%"></div>
                        </div>
                        <span class="progress-text">Complete</span>
                    </div>
                </div>
                <div class="requirement-item">
                    <span class="req-name">Ethics & Professional Conduct</span>
                    <div class="req-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 80%"></div>
                        </div>
                        <span class="progress-text">8/10 hours</span>
                    </div>
                </div>
            </div>
            <div class="urgent-actions">
                <h4>Urgent Actions</h4>
                <ul>
                    <li>Complete Ethics module by Jan 15, 2024</li>
                    <li>Schedule board certification review</li>
                </ul>
            </div>
        </div>
    </div>
    """

def render_active_programs_section() -> str:
    """Render active training programs section."""
    return """
    <div class="dashboard-section active-programs">
        <div class="section-header">
            <h3>Active Training Programs</h3>
            <button class="btn btn-primary" onclick="enrollNewProgram()">Enroll in Program</button>
        </div>
        <div class="programs-grid">
            <div class="program-card">
                <div class="program-header">
                    <h4>Bariatric Surgery Fellowship</h4>
                    <span class="program-status active">Active</span>
                </div>
                <div class="program-details">
                    <p><strong>Institution:</strong> Cleveland Clinic</p>
                    <p><strong>Duration:</strong> 12 months</p>
                    <p><strong>Progress:</strong> Month 8 of 12</p>
                    <p><strong>Next Milestone:</strong> Research Presentation</p>
                </div>
                <div class="program-actions">
                    <button class="btn btn-sm btn-primary">View Progress</button>
                    <button class="btn btn-sm btn-outline">Schedule Mentor Meeting</button>
                </div>
            </div>
            
            <div class="program-card">
                <div class="program-header">
                    <h4>Robotic Surgery Certification</h4>
                    <span class="program-status pending">Starting Soon</span>
                </div>
                <div class="program-details">
                    <p><strong>Institution:</strong> da Vinci Training Center</p>
                    <p><strong>Duration:</strong> 6 weeks</p>
                    <p><strong>Start Date:</strong> Feb 1, 2024</p>
                    <p><strong>Prerequisites:</strong> Completed</p>
                </div>
                <div class="program-actions">
                    <button class="btn btn-sm btn-primary">Prepare for Program</button>
                    <button class="btn btn-sm btn-outline">Contact Coordinator</button>
                </div>
            </div>
        </div>
    </div>
    """

def render_surgery_outcome_integration_section() -> str:
    """Render surgery outcome integration with education section."""
    return """
    <div class="dashboard-section outcome-integration">
        <div class="section-header">
            <h3>Surgery Outcome Learning Integration</h3>
            <button class="btn btn-secondary" onclick="analyzeOutcomes()">Analyze Recent Outcomes</button>
        </div>
        <div class="integration-content">
            <div class="learning-insights">
                <h4>Learning Insights from Recent Cases</h4>
                <div class="insight-cards">
                    <div class="insight-card">
                        <div class="insight-header">
                            <span class="insight-type">Technique Improvement</span>
                            <span class="insight-priority high">High Priority</span>
                        </div>
                        <p>Analysis of your last 10 laparoscopic procedures suggests focusing on port placement optimization. Consider the advanced techniques course.</p>
                        <div class="insight-actions">
                            <button class="btn btn-sm btn-primary">Enroll in Course</button>
                            <button class="btn btn-sm btn-outline">View Analysis</button>
                        </div>
                    </div>
                    
                    <div class="insight-card">
                        <div class="insight-header">
                            <span class="insight-type">Patient Communication</span>
                            <span class="insight-priority medium">Medium Priority</span>
                        </div>
                        <p>Patient satisfaction scores indicate opportunities to improve pre-operative consultation communication.</p>
                        <div class="insight-actions">
                            <button class="btn btn-sm btn-primary">Find Training</button>
                            <button class="btn btn-sm btn-outline">Review Feedback</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="performance-metrics">
                <h4>Performance-Based Learning Recommendations</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Complication Rate</span>
                        <span class="metric-value">2.1%</span>
                        <span class="metric-trend improving">↓ 0.3%</span>
                        <p class="metric-recommendation">Excellent improvement! Consider sharing your techniques in the peer learning network.</p>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Operative Time</span>
                        <span class="metric-value">45 min</span>
                        <span class="metric-trend stable">→ Same</span>
                        <p class="metric-recommendation">Consider advanced efficiency techniques training to reduce operative time further.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def render_professional_development_section() -> str:
    """Render professional development section."""
    return """
    <div class="dashboard-section professional-development">
        <div class="section-header">
            <h3>Professional Development</h3>
            <button class="btn btn-primary" onclick="createDevelopmentPlan()">Create Development Plan</button>
        </div>
        <div class="development-content">
            <div class="career-pathway">
                <h4>Career Pathway Progress</h4>
                <div class="pathway-timeline">
                    <div class="pathway-milestone completed">
                        <div class="milestone-marker"></div>
                        <div class="milestone-content">
                            <h5>Medical Degree</h5>
                            <p>Johns Hopkins School of Medicine</p>
                            <span class="milestone-date">2018</span>
                        </div>
                    </div>
                    <div class="pathway-milestone completed">
                        <div class="milestone-marker"></div>
                        <div class="milestone-content">
                            <h5>Surgery Residency</h5>
                            <p>General Surgery - Mayo Clinic</p>
                            <span class="milestone-date">2023</span>
                        </div>
                    </div>
                    <div class="pathway-milestone current">
                        <div class="milestone-marker"></div>
                        <div class="milestone-content">
                            <h5>Fellowship Training</h5>
                            <p>Bariatric Surgery - Cleveland Clinic</p>
                            <span class="milestone-date">In Progress</span>
                        </div>
                    </div>
                    <div class="pathway-milestone upcoming">
                        <div class="milestone-marker"></div>
                        <div class="milestone-content">
                            <h5>Board Certification</h5>
                            <p>Bariatric Surgery Specialization</p>
                            <span class="milestone-date">2024</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="development-goals">
                <h4>Development Goals</h4>
                <div class="goals-list">
                    <div class="goal-item">
                        <div class="goal-header">
                            <h5>Complete Robotic Surgery Certification</h5>
                            <span class="goal-deadline">By Q2 2024</span>
                        </div>
                        <div class="goal-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 25%"></div>
                            </div>
                            <span class="progress-text">25% Complete</span>
                        </div>
                        <div class="goal-actions">
                            <button class="btn btn-sm btn-primary">Update Progress</button>
                            <button class="btn btn-sm btn-outline">View Plan</button>
                        </div>
                    </div>
                    
                    <div class="goal-item">
                        <div class="goal-header">
                            <h5>Publish Research Paper on Bariatric Outcomes</h5>
                            <span class="goal-deadline">By Dec 2024</span>
                        </div>
                        <div class="goal-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 60%"></div>
                            </div>
                            <span class="progress-text">60% Complete</span>
                        </div>
                        <div class="goal-actions">
                            <button class="btn btn-sm btn-primary">Update Progress</button>
                            <button class="btn btn-sm btn-outline">View Plan</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def render_education_javascript() -> str:
    """Generate JavaScript for education dashboard interactions."""
    return """
    <script>
    // Education Dashboard JavaScript Functions
    
    function viewDetailedProgress() {
        // Navigate to detailed training progress view
        window.location.href = '/education/progress/detailed';
    }
    
    function scheduleTraining() {
        // Open training scheduling modal
        $('#trainingScheduleModal').modal('show');
    }
    
    function manageCertifications() {
        // Navigate to certification management
        window.location.href = '/education/certifications';
    }
    
    function renewCertification() {
        // Open certification renewal process
        $('#certificationRenewalModal').modal('show');
    }
    
    function viewAllCourses() {
        // Navigate to course catalog
        window.location.href = '/education/courses';
    }
    
    function enrollNewProgram() {
        // Open program enrollment wizard
        $('#programEnrollmentModal').modal('show');
    }
    
    function analyzeOutcomes() {
        // Trigger surgery outcome analysis for learning
        fetch('/api/v1/education/analyze-outcomes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Analysis complete! New learning recommendations available.', 'success');
                location.reload();
            }
        })
        .catch(error => {
            showNotification('Failed to analyze outcomes: ' + error.message, 'error');
        });
    }
    
    function createDevelopmentPlan() {
        // Open development plan creation wizard
        $('#developmentPlanModal').modal('show');
    }
    
    function showNotification(message, type) {
        // Show toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    // Initialize dashboard when page loads
    document.addEventListener('DOMContentLoaded', function() {
        // Load real-time data
        loadEducationMetrics();
        
        // Set up periodic updates
        setInterval(loadEducationMetrics, 300000); // Update every 5 minutes
    });
    
    function loadEducationMetrics() {
        fetch('/api/v1/education/metrics', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDashboardMetrics(data.metrics);
            }
        })
        .catch(error => {
            console.error('Failed to load education metrics:', error);
        });
    }
    
    function updateDashboardMetrics(metrics) {
        // Update progress indicators
        document.querySelectorAll('.progress-circle').forEach(circle => {
            const progress = metrics.overall_progress || 75;
            circle.setAttribute('data-progress', progress);
            circle.querySelector('.progress-text').textContent = progress + '%';
        });
        
        // Update skill progress bars
        if (metrics.skill_assessments) {
            Object.entries(metrics.skill_assessments).forEach(([skill, progress]) => {
                const skillElement = document.querySelector(`[data-skill="${skill}"] .skill-progress`);
                if (skillElement) {
                    skillElement.style.width = progress + '%';
                }
            });
        }
    }
    </script>
    """
