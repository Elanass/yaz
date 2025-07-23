# Gastric ADCI Platform - API Documentation

## Overview

The Gastric ADCI Platform provides a comprehensive REST API for cohort management and clinical decision support. This API enables integration with Electronic Health Records (EHR), research databases, and other healthcare systems.

**Base URL**: `https://your-platform-url.com/api/v1`
**Authentication**: Bearer Token (JWT)
**Content-Type**: `application/json`

---

## Authentication

### Get Access Token
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "role": "researcher"
  }
}
```

### Using the Token
Include the token in all subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Cohort Management

### Create Cohort Study

```http
POST /cohorts/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

{
  "study_name": "My Research Cohort",
  "description": "Testing new treatment protocols",
  "format_type": "csv",
  "engine_name": "adci",
  "confidence_threshold": 0.75,
  "include_alternatives": true,
  "file": [CSV file data]
}
```

**Response:**
```json
{
  "id": "cohort-uuid",
  "study_name": "My Research Cohort",
  "status": "validating",
  "total_patients": 0,
  "engine_name": "adci",
  "created_at": "2025-07-23T10:30:00Z"
}
```

### List Cohort Studies

```http
GET /cohorts?status=completed&limit=50&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "cohort-uuid-1",
    "study_name": "Gastric Cancer Study 2025",
    "status": "completed",
    "total_patients": 150,
    "engine_name": "adci",
    "created_at": "2025-07-20T08:00:00Z",
    "processed_at": "2025-07-20T08:45:00Z"
  }
]
```

### Get Cohort Details

```http
GET /cohorts/{cohort_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "cohort-uuid",
  "study_name": "My Research Cohort",
  "description": "Testing new treatment protocols",
  "status": "completed",
  "total_patients": 50,
  "engine_name": "adci",
  "confidence_threshold": 0.75,
  "created_at": "2025-07-23T10:30:00Z",
  "processed_at": "2025-07-23T11:15:00Z",
  "metadata": {
    "processing_time_minutes": 45,
    "success_rate": 0.96
  }
}
```

### Add Patients to Cohort

```http
POST /cohorts/{cohort_id}/patients
Content-Type: application/json
Authorization: Bearer {token}

[
  {
    "patient_id": "PT001",
    "age": 65,
    "gender": "male",
    "clinical_parameters": {
      "tumor_stage": "T2N1M0",
      "histology": "adenocarcinoma",
      "ecog_score": 1,
      "comorbidities": ["diabetes"]
    }
  }
]
```

### Start Batch Processing

```http
POST /cohorts/{cohort_id}/process
Content-Type: application/json
Authorization: Bearer {token}

{
  "session_name": "Initial Analysis Run",
  "engine_parameters": {
    "confidence_threshold": 0.8,
    "include_alternatives": true
  }
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "status": "processing",
  "total_patients": 50,
  "processed_patients": 0,
  "estimated_completion": "2025-07-23T12:00:00Z"
}
```

---

## Results and Analysis

### Get Processing Sessions

```http
GET /cohorts/{cohort_id}/sessions
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "session-uuid",
    "session_name": "Initial Analysis Run",
    "status": "completed",
    "total_patients": 50,
    "processed_patients": 50,
    "failed_patients": 0,
    "processing_start_time": "2025-07-23T11:00:00Z",
    "processing_end_time": "2025-07-23T11:45:00Z",
    "summary_stats": {
      "avg_confidence": 0.82,
      "high_confidence_count": 38,
      "medium_confidence_count": 10,
      "low_confidence_count": 2
    }
  }
]
```

### Get Session Results

```http
GET /cohorts/sessions/{session_id}/results?limit=100&offset=0
Authorization: Bearer {token}
```

**Query Parameters:**
- `risk_threshold`: Filter by minimum risk score (0.0-1.0)
- `confidence_threshold`: Filter by minimum confidence (0.0-1.0)
- `protocol_filter`: Filter by protocol type
- `limit`: Number of results (max 1000)
- `offset`: Pagination offset

**Response:**
```json
[
  {
    "id": "result-uuid",
    "patient_id": "PT001",
    "engine_name": "adci",
    "engine_version": "2.1.0",
    "recommendation": {
      "type": "neoadjuvant_therapy",
      "protocol": "FLOT",
      "surgery": "D2_gastrectomy"
    },
    "confidence_score": 0.85,
    "confidence_level": "high",
    "risk_score": 0.4,
    "risk_level": "medium",
    "evidence_summary": [
      {
        "evidence_id": "E001",
        "level": "1",
        "description": "FLOT superior to ECF in perioperative setting",
        "citation": "Al-Batran et al. Lancet 2019"
      }
    ],
    "reasoning_chain": [
      {
        "step": 1,
        "factor": "tumor_staging",
        "reasoning": "T2N1 staging indicates locally advanced disease"
      }
    ],
    "alternative_options": [
      {
        "treatment": "Surgery first with adjuvant therapy",
        "confidence": 0.72,
        "rationale": "Alternative for patients intolerant to neoadjuvant"
      }
    ],
    "warnings": [],
    "processing_time_ms": 150.5,
    "created_at": "2025-07-23T11:15:00Z"
  }
]
```

### Get Session Summary

```http
GET /cohorts/sessions/{session_id}/summary
Authorization: Bearer {token}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "total_patients": 50,
  "processed_patients": 50,
  "success_rate": 0.96,
  "processing_time_minutes": 45,
  "confidence_distribution": {
    "high": {"count": 38, "percentage": 76.0},
    "medium": {"count": 10, "percentage": 20.0},
    "low": {"count": 2, "percentage": 4.0}
  },
  "risk_distribution": {
    "low": {"count": 20, "percentage": 40.0},
    "medium": {"count": 25, "percentage": 50.0},
    "high": {"count": 5, "percentage": 10.0}
  },
  "protocol_distribution": {
    "neoadjuvant_therapy": 30,
    "surgery_first": 15,
    "palliative": 5
  },
  "average_scores": {
    "confidence": 0.82,
    "risk": 0.45
  }
}
```

---

## Export and Reports

### Create Export Task

```http
POST /cohorts/sessions/{session_id}/export
Content-Type: application/json
Authorization: Bearer {token}

{
  "export_format": "csv",
  "filters": {
    "confidence_threshold": 0.7,
    "include_alternatives": true
  },
  "options": {
    "include_summary": true,
    "include_evidence": true
  }
}
```

**Response:**
```json
{
  "export_id": "export-uuid",
  "status": "processing",
  "estimated_completion": "2025-07-23T12:05:00Z"
}
```

### Check Export Status

```http
GET /cohorts/exports/{export_id}/status
Authorization: Bearer {token}
```

**Response:**
```json
{
  "export_id": "export-uuid",
  "status": "completed",
  "progress": 100,
  "file_size": 2048576,
  "created_at": "2025-07-23T12:00:00Z",
  "completed_at": "2025-07-23T12:03:00Z"
}
```

### Download Export

```http
GET /cohorts/exports/{export_id}/download
Authorization: Bearer {token}
```

**Response:** File download with appropriate Content-Type header

---

## Decision Engine Direct Access

### Process Single Patient

```http
POST /decision-engine/process
Content-Type: application/json
Authorization: Bearer {token}

{
  "engine_name": "adci",
  "patient_id": "PT001",
  "clinical_parameters": {
    "tumor_stage": "T2N1M0",
    "histology": "adenocarcinoma",
    "ecog_score": 1,
    "age": 65,
    "comorbidities": ["diabetes"]
  },
  "context": {
    "institution": "Memorial Hospital",
    "urgency": "routine"
  },
  "include_alternatives": true,
  "confidence_threshold": 0.75
}
```

**Response:**
```json
{
  "engine_name": "adci",
  "engine_version": "2.1.0",
  "patient_id": "PT001",
  "recommendation": {
    "type": "neoadjuvant_therapy",
    "protocol": "FLOT",
    "surgery": "D2_gastrectomy",
    "duration_weeks": 8
  },
  "confidence_score": 0.85,
  "confidence_level": "high",
  "evidence_summary": [...],
  "reasoning_chain": [...],
  "alternative_options": [...],
  "risk_assessment": {
    "surgical_risk": "low",
    "treatment_toxicity": "moderate",
    "overall_prognosis": "good"
  },
  "monitoring_recommendations": {
    "imaging_schedule": "every_3_months",
    "lab_monitoring": "weekly_during_treatment"
  },
  "warnings": [],
  "data_completeness": 0.95,
  "processing_time_ms": 150.5
}
```

### Get Available Engines

```http
GET /decision-engine/engines
Authorization: Bearer {token}
```

**Response:**
```json
{
  "engines": [
    {
      "name": "adci",
      "display_name": "ADCI (Adaptive Decision Confidence Index)",
      "description": "Adaptive decision support with confidence scoring",
      "version": "2.1.0",
      "indication": "Gastric cancer treatment decisions",
      "parameters": [
        "tumor_stage", "histology", "biomarkers", 
        "performance_status", "comorbidities"
      ]
    },
    {
      "name": "gastrectomy",
      "display_name": "Gastrectomy Planning Engine",
      "description": "Surgical approach and technique recommendations",
      "version": "1.5.2",
      "indication": "Gastric resection procedures"
    }
  ]
}
```

---

## Hypothesis Testing

### Create Hypothesis

```http
POST /cohorts/sessions/{session_id}/hypotheses
Content-Type: application/json
Authorization: Bearer {token}

{
  "hypothesis_name": "ECOG Score Impact on Confidence",
  "description": "Analyze how ECOG score affects treatment recommendation confidence",
  "hypothesis_type": "correlation",
  "parameters": {
    "independent_variable": "ecog_score",
    "dependent_variable": "confidence_score",
    "control_variables": ["age", "tumor_stage"]
  }
}
```

**Response:**
```json
{
  "id": "hypothesis-uuid",
  "hypothesis_name": "ECOG Score Impact on Confidence",
  "status": "analyzing",
  "created_at": "2025-07-23T12:10:00Z"
}
```

### Get Hypothesis Results

```http
GET /cohorts/hypotheses/{hypothesis_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "hypothesis-uuid",
  "hypothesis_name": "ECOG Score Impact on Confidence",
  "status": "completed",
  "results": {
    "correlation_coefficient": -0.23,
    "p_value": 0.045,
    "statistical_significance": true,
    "confidence_interval": [-0.45, -0.01],
    "sample_size": 50,
    "interpretation": "Weak negative correlation between ECOG score and confidence"
  },
  "visualizations": {
    "scatter_plot_url": "/api/v1/hypotheses/{id}/charts/scatter",
    "distribution_chart_url": "/api/v1/hypotheses/{id}/charts/distribution"
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid clinical parameters format",
    "details": {
      "field": "clinical_parameters.tumor_stage",
      "issue": "Invalid TNM staging format"
    },
    "timestamp": "2025-07-23T12:00:00Z",
    "request_id": "req-uuid"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or expired token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `NOT_FOUND` | 404 | Resource not found |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## Rate Limits

- **Authentication**: 5 requests per minute
- **Cohort Upload**: 10 uploads per hour
- **Batch Processing**: 3 concurrent sessions
- **Single Patient Processing**: 100 requests per minute
- **Export Generation**: 5 exports per hour

Rate limit headers included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1690112400
```

---

## SDKs and Integration Examples

### Python SDK Example

```python
from gastric_adci_client import GastricADCIClient

# Initialize client
client = GastricADCIClient(
    base_url="https://your-platform-url.com/api/v1",
    token="your-jwt-token"
)

# Create cohort
cohort = client.cohorts.create(
    study_name="API Test Cohort",
    engine_name="adci",
    patients=[
        {
            "patient_id": "API001",
            "age": 65,
            "gender": "male",
            "clinical_parameters": {
                "tumor_stage": "T2N1M0",
                "histology": "adenocarcinoma"
            }
        }
    ]
)

# Process cohort
session = client.cohorts.process(cohort.id)

# Wait for completion and get results
results = client.sessions.wait_for_completion(session.id)
print(f"Processed {len(results)} patients")
```

### JavaScript/Node.js Example

```javascript
const { GastricADCIClient } = require('@gastric-adci/client');

const client = new GastricADCIClient({
  baseURL: 'https://your-platform-url.com/api/v1',
  token: 'your-jwt-token'
});

// Process single patient
const result = await client.decisionEngine.process({
  engine_name: 'adci',
  patient_id: 'JS001',
  clinical_parameters: {
    tumor_stage: 'T2N1M0',
    histology: 'adenocarcinoma',
    ecog_score: 1
  }
});

console.log('Recommendation:', result.recommendation);
console.log('Confidence:', result.confidence_score);
```

---

## Webhooks

### Configure Webhook

```http
POST /webhooks
Content-Type: application/json
Authorization: Bearer {token}

{
  "url": "https://your-server.com/webhook",
  "events": ["cohort.processing.completed", "export.completed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

- `cohort.processing.started`
- `cohort.processing.completed`
- `cohort.processing.failed`
- `export.completed`
- `hypothesis.completed`

### Webhook Payload Example

```json
{
  "event": "cohort.processing.completed",
  "timestamp": "2025-07-23T12:00:00Z",
  "data": {
    "cohort_id": "cohort-uuid",
    "session_id": "session-uuid",
    "total_patients": 50,
    "processed_patients": 50,
    "processing_time_minutes": 45
  },
  "signature": "sha256=hash"
}
```

---

## Support

- **API Documentation**: Available at `/api/docs` (Swagger UI)
- **Technical Support**: api-support@gastric-adci.health
- **Rate Limit Increases**: Contact support for higher limits
- **Custom Integration**: Professional services available

For more examples and detailed integration guides, visit our [Developer Portal](https://developers.gastric-adci.health).
