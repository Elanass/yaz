<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Gastric ADCI Platform

## Project Context
This is a healthcare-grade Progressive Web App (PWA) for gastric oncology-surgery decision support using the ADCI (Adaptive Decision Confidence Index) framework.

## Technology Stack
- **Backend**: FastAPI, PostgreSQL, ElectricsQL, IPFS
- **Frontend**: FastHTML, HTMX, Gun.js for reactive state
- **Deployment**: Google Cloud Run/GKE, Docker
- **Compliance**: HIPAA, GDPR with audit trails

## Code Guidelines

### Security & Compliance
- Always implement proper input validation and sanitization
- Use encryption for sensitive clinical data
- Include audit logging for all data access and modifications
- Follow HIPAA/GDPR compliance patterns
- Implement proper RBAC (Role-Based Access Control)

### Architecture Patterns
- Follow modular, DRY principles
- Use dependency injection for services
- Implement proper error handling with clinical context
- Use async/await patterns for database operations
- Follow RESTful API design with proper HTTP status codes

### Clinical Domain
- Understand that this handles sensitive medical data
- Decision engines (ADCI, Gastrectomy, FLOT) require high accuracy
- Always include confidence intervals and uncertainty measures
- Implement proper validation for clinical protocols
- Use evidence-based scoring and recommendations

### Frontend Development
- Build responsive, mobile-first PWA components
- Implement offline-first patterns with ElectricsQL
- Use HTMX for reactive UI without heavy JavaScript
- Follow accessibility standards (WCAG 2.1 AA)
- Optimize for healthcare professional workflows

### Database & Data
- Use ElectricsQL-compatible schema design
- Implement proper indexing for clinical queries
- Handle time-series data for patient tracking
- Use IPFS for immutable evidence storage
- Implement proper data retention policies

### Testing
- Write comprehensive unit tests for decision engines
- Include integration tests for clinical workflows
- Test offline functionality and sync scenarios
- Validate compliance with healthcare standards
- Performance test for sub-200ms API responses

### Performance
- Target <200ms API response times
- Optimize for offline-first PWA functionality
- Use proper caching strategies
- Implement efficient database queries
- Consider medical emergency response times

## Naming Conventions
- Use clinical terminology accurately
- Follow PascalCase for classes, snake_case for functions
- Use descriptive names for medical entities
- Include units in variable names (e.g., `dosage_mg`)
- Use proper medical abbreviations consistently

## Error Handling
- Provide clear, actionable error messages
- Log errors with proper clinical context
- Implement graceful degradation for offline scenarios
- Handle medical data validation errors appropriately
- Include help text for clinical users

Remember: This platform directly impacts patient care. Prioritize accuracy, security, and reliability in all code contributions.
