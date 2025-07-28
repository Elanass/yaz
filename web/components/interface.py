"""
Simple Web Interface Components
Clean, reusable components for the web interface
"""

from typing import Any, Dict, List, Optional


def create_page_layout(title: str, content: str, navigation: Optional[List[Dict[str, str]]] = None) -> str:
    """Create basic page layout"""
    
    nav_links = ""
    if navigation:
        nav_items = []
        for item in navigation:
            nav_items.append(f'<a href="{item["url"]}" class="nav-link">{item["text"]}</a>')
        nav_links = " | ".join(nav_items)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Gastric ADCI Platform</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8fafc;
            }}
            .header {{
                background-color: #2563eb;
                color: white;
                padding: 1rem 2rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 1.5rem;
                font-weight: 600;
            }}
            .nav {{
                margin-top: 0.5rem;
                font-size: 0.9rem;
            }}
            .nav-link {{
                color: #dbeafe;
                text-decoration: none;
                margin-right: 1rem;
            }}
            .nav-link:hover {{
                color: white;
                text-decoration: underline;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }}
            .btn {{
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{
                background-color: #1d4ed8;
            }}
            .btn-secondary {{
                background-color: #64748b;
            }}
            .btn-secondary:hover {{
                background-color: #475569;
            }}
            .form-group {{
                margin-bottom: 1rem;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 0.25rem;
                font-weight: 500;
            }}
            .form-group input, .form-group select, .form-group textarea {{
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 0.9rem;
            }}
            .alert {{
                padding: 1rem;
                border-radius: 6px;
                margin-bottom: 1rem;
            }}
            .alert-success {{
                background-color: #dcfce7;
                color: #166534;
                border: 1px solid #bbf7d0;
            }}
            .alert-error {{
                background-color: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
            }}
        </style>
    </head>
    <body>
        <header class="header">
            <h1>🏥 Gastric ADCI Platform</h1>
            <nav class="nav">
                {nav_links}
            </nav>
        </header>
        <main class="container">
            {content}
        </main>
    </body>
    </html>
    """


def create_decision_form() -> str:
    """Create decision analysis form"""
    
    return """
    <div class="card">
        <h2>Clinical Decision Analysis</h2>
        <form id="decision-form">
            <div class="form-group">
                <label for="engine_type">Decision Engine:</label>
                <select id="engine_type" name="engine_type" required>
                    <option value="">Select Engine</option>
                    <option value="adci">ADCI - Treatment Recommendation</option>
                    <option value="gastrectomy">Gastrectomy - Surgical Planning</option>
                </select>
            </div>
            
            <h3>Patient Information</h3>
            <div class="grid">
                <div class="form-group">
                    <label for="age">Age (years):</label>
                    <input type="number" id="age" name="age" min="0" max="150" required>
                </div>
                <div class="form-group">
                    <label for="performance_status">Performance Status (ECOG):</label>
                    <select id="performance_status" name="performance_status" required>
                        <option value="">Select Status</option>
                        <option value="0">0 - Fully active</option>
                        <option value="1">1 - Restricted strenuous activity</option>
                        <option value="2">2 - Ambulatory, capable of self-care</option>
                        <option value="3">3 - Limited self-care</option>
                        <option value="4">4 - Completely disabled</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="bmi">BMI:</label>
                    <input type="number" id="bmi" name="bmi" step="0.1" min="10" max="60">
                </div>
            </div>
            
            <h3>Tumor Characteristics</h3>
            <div class="grid">
                <div class="form-group">
                    <label for="stage">TNM Stage:</label>
                    <select id="stage" name="stage" required>
                        <option value="">Select Stage</option>
                        <option value="T1aN0M0">T1aN0M0</option>
                        <option value="T1bN0M0">T1bN0M0</option>
                        <option value="T2N0M0">T2N0M0</option>
                        <option value="T3N0M0">T3N0M0</option>
                        <option value="T3N1M0">T3N1M0</option>
                        <option value="T3N2M0">T3N2M0</option>
                        <option value="T4aN1M0">T4aN1M0</option>
                        <option value="T4aN2M0">T4aN2M0</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="location">Tumor Location:</label>
                    <select id="location" name="location" required>
                        <option value="">Select Location</option>
                        <option value="cardia">Cardia</option>
                        <option value="fundus">Fundus</option>
                        <option value="body">Body</option>
                        <option value="antrum">Antrum</option>
                        <option value="pylorus">Pylorus</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="size_cm">Tumor Size (cm):</label>
                    <input type="number" id="size_cm" name="size_cm" step="0.1" min="0" max="20">
                </div>
                <div class="form-group">
                    <label for="histology">Histology:</label>
                    <select id="histology" name="histology">
                        <option value="">Select Histology</option>
                        <option value="adenocarcinoma">Adenocarcinoma</option>
                        <option value="signet_ring">Signet Ring Cell</option>
                        <option value="mucinous">Mucinous</option>
                        <option value="mixed">Mixed</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <button type="submit" class="btn">Analyze Decision</button>
                <button type="button" class="btn btn-secondary" onclick="clearForm()">Clear Form</button>
            </div>
        </form>
        
        <div id="result" style="display: none;"></div>
    </div>
    
    <script>
        document.getElementById('decision-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                engine_type: formData.get('engine_type'),
                patient_data: {
                    age: parseInt(formData.get('age')),
                    performance_status: parseInt(formData.get('performance_status')),
                    bmi: formData.get('bmi') ? parseFloat(formData.get('bmi')) : null
                },
                tumor_data: {
                    stage: formData.get('stage'),
                    location: formData.get('location'),
                    size_cm: formData.get('size_cm') ? parseFloat(formData.get('size_cm')) : null,
                    histology: formData.get('histology')
                }
            };
            
            // Remove null values
            Object.keys(data.patient_data).forEach(key => {
                if (data.patient_data[key] === null || data.patient_data[key] === '') {
                    delete data.patient_data[key];
                }
            });
            Object.keys(data.tumor_data).forEach(key => {
                if (data.tumor_data[key] === null || data.tumor_data[key] === '') {
                    delete data.tumor_data[key];
                }
            });
            
            try {
                // First try to get a token (for demo, use admin credentials)
                const loginResponse = await fetch('/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'admin@gastric-adci.com',
                        password: 'admin123'
                    })
                });
                
                if (!loginResponse.ok) {
                    throw new Error('Authentication failed');
                }
                
                const loginData = await loginResponse.json();
                const token = loginData.data.access_token;
                
                // Make decision request
                const response = await fetch('/api/v1/decisions/analyze', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayResult(result.data);
                } else {
                    displayError(result.detail || 'Analysis failed');
                }
                
            } catch (error) {
                displayError('Network error: ' + error.message);
            }
        });
        
        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            const confidence = (data.confidence_score * 100).toFixed(1);
            
            let recommendationHtml = '<h4>Recommendation:</h4><ul>';
            Object.entries(data.recommendation).forEach(([key, value]) => {
                recommendationHtml += `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`;
            });
            recommendationHtml += '</ul>';
            
            let reasoningHtml = '<h4>Clinical Reasoning:</h4><ul>';
            data.reasoning.forEach(reason => {
                reasoningHtml += `<li>${reason}</li>`;
            });
            reasoningHtml += '</ul>';
            
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h3>Analysis Complete</h3>
                    <p><strong>Confidence Level:</strong> ${data.confidence_level} (${confidence}%)</p>
                    ${recommendationHtml}
                    ${reasoningHtml}
                    <p><em>Decision ID: ${data.decision_id}</em></p>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        function displayError(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <h3>Analysis Failed</h3>
                    <p>${message}</p>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        function clearForm() {
            document.getElementById('decision-form').reset();
            document.getElementById('result').style.display = 'none';
        }
    </script>
    """


def create_dashboard() -> str:
    """Create simple dashboard"""
    
    return """
    <div class="grid">
        <div class="card">
            <h3>🧠 Decision Engines</h3>
            <p>AI-powered clinical decision support</p>
            <a href="/decision" class="btn">New Analysis</a>
        </div>
        
        <div class="card">
            <h3>📊 Recent Decisions</h3>
            <p>View your recent decision analyses</p>
            <a href="/decisions" class="btn btn-secondary">View All</a>
        </div>
        
        <div class="card">
            <h3>📚 Guidelines</h3>
            <p>Evidence-based clinical protocols</p>
            <a href="/guidelines" class="btn btn-secondary">Browse</a>
        </div>
        
        <div class="card">
            <h3>⚙️ Settings</h3>
            <p>Configure your preferences</p>
            <a href="/settings" class="btn btn-secondary">Configure</a>
        </div>
    </div>
    
    <div class="card">
        <h3>System Status</h3>
        <div id="health-status">Loading...</div>
    </div>
    
    <script>
        async function loadHealthStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                if (data.success) {
                    const health = data.data;
                    let statusHtml = `<p><strong>Status:</strong> ${health.status}</p>`;
                    statusHtml += `<p><strong>Version:</strong> ${health.version}</p>`;
                    statusHtml += `<p><strong>Environment:</strong> ${health.environment}</p>`;
                    
                    if (health.components) {
                        statusHtml += '<h4>Components:</h4><ul>';
                        Object.entries(health.components).forEach(([name, status]) => {
                            const icon = status === 'healthy' ? '✅' : '❌';
                            statusHtml += `<li>${icon} ${name}: ${status}</li>`;
                        });
                        statusHtml += '</ul>';
                    }
                    
                    document.getElementById('health-status').innerHTML = statusHtml;
                } else {
                    document.getElementById('health-status').innerHTML = '<p>❌ Health check failed</p>';
                }
            } catch (error) {
                document.getElementById('health-status').innerHTML = '<p>❌ Unable to check system status</p>';
            }
        }
        
        loadHealthStatus();
    </script>
    """
