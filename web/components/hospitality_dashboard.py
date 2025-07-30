"""
Hospitality dashboard components for YAZ Surgery Analytics Platform.
Provides UI components for patient experience and hospitality management.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

def render_hospitality_dashboard(user_data: Dict[str, Any]) -> str:
    """Render main hospitality dashboard."""
    return f"""
    <div class="hospitality-dashboard">
        <div class="dashboard-header">
            <h2>Patient Hospitality & Experience</h2>
            <div class="user-info">
                <span>Welcome, {user_data.get('name', 'User')}</span>
                <span class="role-badge">{user_data.get('role', 'Hospitality Coordinator')}</span>
            </div>
        </div>
        
        <div class="dashboard-grid">
            {render_patient_experience_card()}
            {render_accommodation_status_card()}
            {render_service_requests_card()}
            {render_satisfaction_metrics_card()}
        </div>
        
        <div class="dashboard-sections">
            {render_active_plans_section()}
            {render_family_services_section()}
            {render_dietary_management_section()}
            {render_transportation_coordination_section()}
        </div>
    </div>
    """

def render_patient_experience_card() -> str:
    """Render patient experience overview card."""
    return """
    <div class="dashboard-card patient-experience">
        <div class="card-header">
            <h3>Patient Experience</h3>
            <div class="experience-score">
                <div class="score-circle" data-score="4.7">
                    <span class="score-text">4.7</span>
                    <span class="score-max">/5.0</span>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div class="experience-metrics">
                <div class="metric-item">
                    <span class="metric-label">Overall Satisfaction</span>
                    <div class="metric-bar">
                        <div class="metric-progress" style="width: 94%"></div>
                    </div>
                    <span class="metric-value">94%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Accommodation Quality</span>
                    <div class="metric-bar">
                        <div class="metric-progress" style="width: 91%"></div>
                    </div>
                    <span class="metric-value">91%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Service Responsiveness</span>
                    <div class="metric-bar">
                        <div class="metric-progress" style="width: 88%"></div>
                    </div>
                    <span class="metric-value">88%</span>
                </div>
            </div>
            <div class="recent-feedback">
                <h4>Recent Feedback</h4>
                <div class="feedback-item positive">
                    <span class="feedback-rating">★★★★★</span>
                    <p>"Excellent service and comfortable accommodation!"</p>
                    <span class="feedback-patient">Patient #P12345</span>
                </div>
            </div>
        </div>
    </div>
    """

def render_accommodation_status_card() -> str:
    """Render accommodation status card."""
    return """
    <div class="dashboard-card accommodation-status">
        <div class="card-header">
            <h3>Accommodation Status</h3>
            <span class="occupancy-rate">78.5% Occupied</span>
        </div>
        <div class="card-body">
            <div class="accommodation-overview">
                <div class="facility-stats">
                    <div class="stat-item">
                        <span class="stat-number">133</span>
                        <span class="stat-label">Occupied Rooms</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">37</span>
                        <span class="stat-label">Available Rooms</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">170</span>
                        <span class="stat-label">Total Capacity</span>
                    </div>
                </div>
                <div class="room-types">
                    <div class="room-type-item">
                        <span class="room-type">Standard Rooms</span>
                        <div class="room-availability">
                            <span class="available">30</span>/<span class="total">80</span>
                        </div>
                    </div>
                    <div class="room-type-item">
                        <span class="room-type">Suites</span>
                        <div class="room-availability">
                            <span class="available">5</span>/<span class="total">30</span>
                        </div>
                    </div>
                    <div class="room-type-item">
                        <span class="room-type">Accessible Rooms</span>
                        <div class="room-availability">
                            <span class="available">2</span>/<span class="total">10</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="manageRooms()">Manage Rooms</button>
                <button class="btn btn-secondary" onclick="viewOccupancy()">View Occupancy</button>
            </div>
        </div>
    </div>
    """

def render_service_requests_card() -> str:
    """Render service requests card."""
    return """
    <div class="dashboard-card service-requests">
        <div class="card-header">
            <h3>Service Requests</h3>
            <span class="request-count">23 Today</span>
        </div>
        <div class="card-body">
            <div class="request-summary">
                <div class="request-type">
                    <span class="type-name">Concierge Services</span>
                    <span class="type-count">8</span>
                </div>
                <div class="request-type">
                    <span class="type-name">Dining Services</span>
                    <span class="type-count">6</span>
                </div>
                <div class="request-type">
                    <span class="type-name">Transportation</span>
                    <span class="type-count">5</span>
                </div>
                <div class="request-type">
                    <span class="type-name">Family Support</span>
                    <span class="type-count">4</span>
                </div>
            </div>
            <div class="urgent-requests">
                <h4>Urgent Requests</h4>
                <div class="urgent-item">
                    <span class="urgency-indicator high"></span>
                    <div class="request-details">
                        <p><strong>Emergency Transportation</strong></p>
                        <p>Patient P12348 - Family emergency</p>
                        <span class="request-time">15 minutes ago</span>
                    </div>
                </div>
                <div class="urgent-item">
                    <span class="urgency-indicator medium"></span>
                    <div class="request-details">
                        <p><strong>Dietary Accommodation</strong></p>
                        <p>Patient P12349 - New allergy discovery</p>
                        <span class="request-time">1 hour ago</span>
                    </div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="viewAllRequests()">View All Requests</button>
                <button class="btn btn-secondary" onclick="createNewRequest()">New Request</button>
            </div>
        </div>
    </div>
    """

def render_satisfaction_metrics_card() -> str:
    """Render satisfaction metrics card."""
    return """
    <div class="dashboard-card satisfaction-metrics">
        <div class="card-header">
            <h3>Satisfaction Metrics</h3>
            <div class="metrics-period">
                <select onchange="updateMetricsPeriod(this.value)">
                    <option value="30">Last 30 Days</option>
                    <option value="7">Last 7 Days</option>
                    <option value="1">Today</option>
                </select>
            </div>
        </div>
        <div class="card-body">
            <div class="satisfaction-breakdown">
                <div class="satisfaction-item">
                    <span class="service-name">Accommodation</span>
                    <div class="rating-stars">★★★★★</div>
                    <span class="rating-score">4.6</span>
                </div>
                <div class="satisfaction-item">
                    <span class="service-name">Dining</span>
                    <div class="rating-stars">★★★★☆</div>
                    <span class="rating-score">4.3</span>
                </div>
                <div class="satisfaction-item">
                    <span class="service-name">Transportation</span>
                    <div class="rating-stars">★★★★★</div>
                    <span class="rating-score">4.8</span>
                </div>
                <div class="satisfaction-item">
                    <span class="service-name">Family Support</span>
                    <div class="rating-stars">★★★★☆</div>
                    <span class="rating-score">4.4</span>
                </div>
            </div>
            <div class="satisfaction-trends">
                <h4>Trends</h4>
                <div class="trend-item">
                    <span class="trend-label">Overall Satisfaction</span>
                    <span class="trend-value improving">↗ +0.3</span>
                </div>
                <div class="trend-item">
                    <span class="trend-label">Response Time</span>
                    <span class="trend-value improving">↗ 15% faster</span>
                </div>
            </div>
        </div>
    </div>
    """

def render_active_plans_section() -> str:
    """Render active hospitality plans section."""
    return """
    <div class="dashboard-section active-plans">
        <div class="section-header">
            <h3>Active Hospitality Plans</h3>
            <button class="btn btn-primary" onclick="createNewPlan()">Create New Plan</button>
        </div>
        <div class="plans-table">
            <table class="table">
                <thead>
                    <tr>
                        <th>Patient</th>
                        <th>Plan ID</th>
                        <th>Service Tier</th>
                        <th>Check-in Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <div class="patient-info">
                                <strong>Sarah Johnson</strong>
                                <small>P12345 • Gastric Bypass</small>
                            </div>
                        </td>
                        <td>HP_20240115_001</td>
                        <td><span class="tier-badge premium">Premium</span></td>
                        <td>Jan 15, 2024</td>
                        <td><span class="status-badge active">Active</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="viewPlan('HP_20240115_001')">View</button>
                            <button class="btn btn-sm btn-primary" onclick="updatePlan('HP_20240115_001')">Update</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <div class="patient-info">
                                <strong>Michael Chen</strong>
                                <small>P12346 • Sleeve Gastrectomy</small>
                            </div>
                        </td>
                        <td>HP_20240115_002</td>
                        <td><span class="tier-badge comfort">Comfort</span></td>
                        <td>Jan 16, 2024</td>
                        <td><span class="status-badge active">Active</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="viewPlan('HP_20240115_002')">View</button>
                            <button class="btn btn-sm btn-primary" onclick="updatePlan('HP_20240115_002')">Update</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <div class="patient-info">
                                <strong>Emily Rodriguez</strong>
                                <small>P12347 • Revision Surgery</small>
                            </div>
                        </td>
                        <td>HP_20240117_003</td>
                        <td><span class="tier-badge vip">VIP</span></td>
                        <td>Jan 17, 2024</td>
                        <td><span class="status-badge pending">Pending</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="viewPlan('HP_20240117_003')">View</button>
                            <button class="btn btn-sm btn-primary" onclick="updatePlan('HP_20240117_003')">Update</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """

def render_family_services_section() -> str:
    """Render family services coordination section."""
    return """
    <div class="dashboard-section family-services">
        <div class="section-header">
            <h3>Family Services Coordination</h3>
            <button class="btn btn-primary" onclick="coordinateFamilyServices()">New Coordination</button>
        </div>
        <div class="family-services-content">
            <div class="service-categories">
                <div class="category-card">
                    <div class="category-header">
                        <h4>Family Accommodation</h4>
                        <span class="active-count">18 Active</span>
                    </div>
                    <div class="category-stats">
                        <div class="stat">
                            <span class="stat-number">45</span>
                            <span class="stat-label">Family Members Served</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">32</span>
                            <span class="stat-label">Rooms Assigned</span>
                        </div>
                    </div>
                    <div class="category-actions">
                        <button class="btn btn-sm btn-primary" onclick="manageFamilyAccommodation()">Manage</button>
                    </div>
                </div>
                
                <div class="category-card">
                    <div class="category-header">
                        <h4>Child Care Services</h4>
                        <span class="active-count">8 Active</span>
                    </div>
                    <div class="category-stats">
                        <div class="stat">
                            <span class="stat-number">12</span>
                            <span class="stat-label">Children in Care</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">6</span>
                            <span class="stat-label">Care Providers</span>
                        </div>
                    </div>
                    <div class="category-actions">
                        <button class="btn btn-sm btn-primary" onclick="manageChildCare()">Manage</button>
                    </div>
                </div>
                
                <div class="category-card">
                    <div class="category-header">
                        <h4>Family Communication</h4>
                        <span class="active-count">25 Active</span>
                    </div>
                    <div class="category-stats">
                        <div class="stat">
                            <span class="stat-number">89</span>
                            <span class="stat-label">Updates Sent Today</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">96%</span>
                            <span class="stat-label">Response Rate</span>
                        </div>
                    </div>
                    <div class="category-actions">
                        <button class="btn btn-sm btn-primary" onclick="manageFamilyCommunication()">Manage</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def render_dietary_management_section() -> str:
    """Render dietary management section."""
    return """
    <div class="dashboard-section dietary-management">
        <div class="section-header">
            <h3>Dietary Management</h3>
            <button class="btn btn-primary" onclick="createDietaryPlan()">New Dietary Plan</button>
        </div>
        <div class="dietary-content">
            <div class="dietary-overview">
                <div class="dietary-stats">
                    <div class="stat-card">
                        <span class="stat-number">156</span>
                        <span class="stat-label">Active Meal Plans</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">23</span>
                        <span class="stat-label">Special Diets</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">98%</span>
                        <span class="stat-label">Meal Satisfaction</span>
                    </div>
                </div>
            </div>
            
            <div class="special-dietary-needs">
                <h4>Special Dietary Requirements</h4>
                <div class="dietary-requirements-list">
                    <div class="requirement-item">
                        <span class="requirement-type">Liquid Diet (Post-Surgery)</span>
                        <span class="patient-count">12 patients</span>
                        <button class="btn btn-sm btn-outline" onclick="manageLiquidDiet()">Manage</button>
                    </div>
                    <div class="requirement-item">
                        <span class="requirement-type">Diabetic Diet</span>
                        <span class="patient-count">8 patients</span>
                        <button class="btn btn-sm btn-outline" onclick="manageDiabeticDiet()">Manage</button>
                    </div>
                    <div class="requirement-item">
                        <span class="requirement-type">Food Allergies</span>
                        <span class="patient-count">15 patients</span>
                        <button class="btn btn-sm btn-outline" onclick="manageAllergies()">Manage</button>
                    </div>
                    <div class="requirement-item">
                        <span class="requirement-type">Cultural/Religious Preferences</span>
                        <span class="patient-count">22 patients</span>
                        <button class="btn btn-sm btn-outline" onclick="manageCulturalDiets()">Manage</button>
                    </div>
                </div>
            </div>
            
            <div class="nutrition-consultations">
                <h4>Nutrition Consultations</h4>
                <div class="consultation-schedule">
                    <div class="consultation-item">
                        <div class="consultation-time">10:00 AM</div>
                        <div class="consultation-details">
                            <strong>Pre-surgery consultation</strong>
                            <p>Patient P12350 - Sarah Williams</p>
                        </div>
                        <div class="consultation-status">Scheduled</div>
                    </div>
                    <div class="consultation-item">
                        <div class="consultation-time">2:00 PM</div>
                        <div class="consultation-details">
                            <strong>Post-surgery follow-up</strong>
                            <p>Patient P12351 - Robert Davis</p>
                        </div>
                        <div class="consultation-status">In Progress</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def render_transportation_coordination_section() -> str:
    """Render transportation coordination section."""
    return """
    <div class="dashboard-section transportation-coordination">
        <div class="section-header">
            <h3>Transportation Coordination</h3>
            <button class="btn btn-primary" onclick="scheduleTransportation()">Schedule Transport</button>
        </div>
        <div class="transportation-content">
            <div class="transport-overview">
                <div class="transport-stats">
                    <div class="stat-item">
                        <span class="stat-number">34</span>
                        <span class="stat-label">Scheduled Today</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">94%</span>
                        <span class="stat-label">On-Time Rate</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">8</span>
                        <span class="stat-label">Active Routes</span>
                    </div>
                </div>
            </div>
            
            <div class="active-transports">
                <h4>Active Transportation</h4>
                <div class="transport-list">
                    <div class="transport-item">
                        <div class="transport-info">
                            <strong>Airport Pickup</strong>
                            <p>Patient P12355 + Family (3)</p>
                            <span class="transport-time">Departure: 11:30 AM</span>
                        </div>
                        <div class="transport-status">
                            <span class="status-badge en-route">En Route</span>
                        </div>
                        <div class="transport-actions">
                            <button class="btn btn-sm btn-outline" onclick="trackTransport('T001')">Track</button>
                            <button class="btn btn-sm btn-secondary" onclick="contactDriver('T001')">Contact</button>
                        </div>
                    </div>
                    
                    <div class="transport-item">
                        <div class="transport-info">
                            <strong>Hospital Discharge</strong>
                            <p>Patient P12356 - Wheelchair Accessible</p>
                            <span class="transport-time">Scheduled: 3:00 PM</span>
                        </div>
                        <div class="transport-status">
                            <span class="status-badge scheduled">Scheduled</span>
                        </div>
                        <div class="transport-actions">
                            <button class="btn btn-sm btn-outline" onclick="viewTransportDetails('T002')">Details</button>
                            <button class="btn btn-sm btn-primary" onclick="modifyTransport('T002')">Modify</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="transport-providers">
                <h4>Transport Providers</h4>
                <div class="provider-grid">
                    <div class="provider-card">
                        <h5>MedTrans Services</h5>
                        <div class="provider-stats">
                            <span class="stat">12 vehicles available</span>
                            <span class="stat">4.8★ rating</span>
                        </div>
                        <div class="provider-services">
                            <span class="service-tag">Wheelchair Accessible</span>
                            <span class="service-tag">Stretcher Transport</span>
                        </div>
                    </div>
                    
                    <div class="provider-card">
                        <h5>Uber Health</h5>
                        <div class="provider-stats">
                            <span class="stat">Real-time tracking</span>
                            <span class="stat">4.7★ rating</span>
                        </div>
                        <div class="provider-services">
                            <span class="service-tag">Standard Rides</span>
                            <span class="service-tag">Prescription Delivery</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def render_hospitality_javascript() -> str:
    """Generate JavaScript for hospitality dashboard interactions."""
    return """
    <script>
    // Hospitality Dashboard JavaScript Functions
    
    function manageRooms() {
        window.location.href = '/hospitality/rooms';
    }
    
    function viewOccupancy() {
        window.location.href = '/hospitality/occupancy';
    }
    
    function viewAllRequests() {
        window.location.href = '/hospitality/requests';
    }
    
    function createNewRequest() {
        $('#serviceRequestModal').modal('show');
    }
    
    function createNewPlan() {
        $('#hospitalityPlanModal').modal('show');
    }
    
    function viewPlan(planId) {
        window.location.href = `/hospitality/plans/${planId}`;
    }
    
    function updatePlan(planId) {
        // Open plan update modal with pre-loaded data
        loadPlanData(planId).then(data => {
            populatePlanModal(data);
            $('#updatePlanModal').modal('show');
        });
    }
    
    function coordinateFamilyServices() {
        $('#familyCoordinationModal').modal('show');
    }
    
    function manageFamilyAccommodation() {
        window.location.href = '/hospitality/family/accommodation';
    }
    
    function manageChildCare() {
        window.location.href = '/hospitality/family/childcare';
    }
    
    function manageFamilyCommunication() {
        window.location.href = '/hospitality/family/communication';
    }
    
    function createDietaryPlan() {
        $('#dietaryPlanModal').modal('show');
    }
    
    function manageLiquidDiet() {
        filterDietaryRequirements('liquid_diet');
    }
    
    function manageDiabeticDiet() {
        filterDietaryRequirements('diabetic');
    }
    
    function manageAllergies() {
        filterDietaryRequirements('allergies');
    }
    
    function manageCulturalDiets() {
        filterDietaryRequirements('cultural');
    }
    
    function scheduleTransportation() {
        $('#transportationModal').modal('show');
    }
    
    function trackTransport(transportId) {
        // Open real-time tracking modal
        $('#transportTrackingModal').modal('show');
        initializeTransportTracking(transportId);
    }
    
    function contactDriver(transportId) {
        // Open driver contact interface
        $('#driverContactModal').modal('show');
        loadDriverInfo(transportId);
    }
    
    function viewTransportDetails(transportId) {
        window.location.href = `/hospitality/transportation/${transportId}`;
    }
    
    function modifyTransport(transportId) {
        loadTransportData(transportId).then(data => {
            populateTransportModal(data);
            $('#modifyTransportModal').modal('show');
        });
    }
    
    function updateMetricsPeriod(days) {
        loadSatisfactionMetrics(days);
    }
    
    // Data loading functions
    async function loadPlanData(planId) {
        const response = await fetch(`/api/v1/hospitality/hospitality-plan/${planId}`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        });
        return response.json();
    }
    
    async function loadTransportData(transportId) {
        const response = await fetch(`/api/v1/hospitality/transportation/${transportId}`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        });
        return response.json();
    }
    
    function loadSatisfactionMetrics(days) {
        fetch(`/api/v1/hospitality/satisfaction-metrics?timeframe_days=${days}`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSatisfactionMetrics(data.satisfaction_report);
            }
        })
        .catch(error => {
            console.error('Failed to load satisfaction metrics:', error);
        });
    }
    
    function updateSatisfactionMetrics(metrics) {
        // Update satisfaction score
        const scoreElement = document.querySelector('.score-text');
        if (scoreElement) {
            scoreElement.textContent = metrics.overall_satisfaction || '4.7';
        }
        
        // Update service area metrics
        if (metrics.service_area_metrics) {
            Object.entries(metrics.service_area_metrics).forEach(([service, score]) => {
                const serviceElement = document.querySelector(`[data-service="${service}"] .rating-score`);
                if (serviceElement) {
                    serviceElement.textContent = score.toFixed(1);
                }
            });
        }
    }
    
    function filterDietaryRequirements(type) {
        // Filter and display dietary requirements by type
        const url = `/hospitality/dietary?filter=${type}`;
        window.location.href = url;
    }
    
    function initializeTransportTracking(transportId) {
        // Initialize real-time transport tracking
        // This would typically connect to a real-time tracking service
        console.log(`Initializing tracking for transport ${transportId}`);
    }
    
    function loadDriverInfo(transportId) {
        // Load driver information for transport
        fetch(`/api/v1/hospitality/transportation/${transportId}/driver`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateDriverInfo(data.driver_info);
            }
        })
        .catch(error => {
            console.error('Failed to load driver info:', error);
        });
    }
    
    function populateDriverInfo(driverInfo) {
        // Populate driver contact modal with driver information
        document.getElementById('driverName').textContent = driverInfo.name;
        document.getElementById('driverPhone').textContent = driverInfo.phone;
        document.getElementById('vehicleInfo').textContent = `${driverInfo.vehicle.make} ${driverInfo.vehicle.model}`;
    }
    
    function populatePlanModal(planData) {
        // Populate plan update modal with existing plan data
        document.getElementById('planPatientId').value = planData.plan.patient_info.patient_id;
        document.getElementById('planServiceTier').value = planData.plan.service_tier;
        // ... populate other fields
    }
    
    function populateTransportModal(transportData) {
        // Populate transport modification modal with existing transport data
        document.getElementById('transportPatientId').value = transportData.transport.patient_id;
        document.getElementById('transportType').value = transportData.transport.transport_type;
        // ... populate other fields
    }
    
    // Initialize dashboard when page loads
    document.addEventListener('DOMContentLoaded', function() {
        loadHospitalityMetrics();
        
        // Set up periodic updates
        setInterval(loadHospitalityMetrics, 300000); // Update every 5 minutes
        
        // Initialize real-time notifications
        initializeNotifications();
    });
    
    function loadHospitalityMetrics() {
        fetch('/api/v1/hospitality/hospitality-dashboard', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDashboardMetrics(data.dashboard);
            }
        })
        .catch(error => {
            console.error('Failed to load hospitality metrics:', error);
        });
    }
    
    function updateDashboardMetrics(dashboard) {
        // Update occupancy rate
        const occupancyElement = document.querySelector('.occupancy-rate');
        if (occupancyElement) {
            occupancyElement.textContent = `${dashboard.accommodation_metrics.occupancy_rate}% Occupied`;
        }
        
        // Update service request count
        const requestCountElement = document.querySelector('.request-count');
        if (requestCountElement) {
            requestCountElement.textContent = `${dashboard.overview.service_requests_today} Today`;
        }
        
        // Update satisfaction score
        const satisfactionElement = document.querySelector('.score-text');
        if (satisfactionElement) {
            satisfactionElement.textContent = dashboard.overview.average_satisfaction.toFixed(1);
        }
    }
    
    function initializeNotifications() {
        // Initialize real-time notifications for urgent requests
        // This would typically use WebSockets or Server-Sent Events
        console.log('Initializing real-time notifications');
    }
    </script>
    """
