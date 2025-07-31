# Decision Precision in Surgery API - Documentation Update

**Version:** 1.1.0  
**Updated:** 2025-07-31  

## New Endpoints

### POST /api/v1/analysis/insights/generate

Generate insights from cohort data

**Request Body:**

```json
{
  "cohort_id": "string",
  "insight_types": [
    "basic_statistics",
    "flot_adherence",
    "albumin_trends",
    "survival_analysis",
    "multivariate_analysis",
    "decision_impact"
  ],
  "notify_email": "string (optional)"
}
```

**Responses:**

- `200`: Insights generated successfully
  ```json
  {
    "id": "string",
    "timestamp": "string (ISO format)",
    "cohort_size": "integer",
    "results": "object with insight data"
  }
  ```

---

### GET /api/v1/analysis/insights/{insight_id}

Get generated insights by ID

**Parameters:**

- `insight_id`: string (path)

**Responses:**

- `200`: Insights retrieved successfully
  ```json
  same as POST response
  ```
- `404`: Insights not found

---

### POST /api/v1/analysis/publication/prepare

Prepare publication from cohort data

**Request Body:**

```json
{
  "cohort_id": "string",
  "publication_type": "string (memoir, article, infographic)",
  "output_format": "string (pdf, docx, html)",
  "title": "string",
  "authors": [
    "string"
  ],
  "notify_email": "string (optional)"
}
```

**Responses:**

- `200`: Publication preparation started
  ```json
  {
    "id": "string",
    "title": "string",
    "type": "string",
    "format": "string",
    "status": "string (processing)",
    "timestamp": "string (ISO format)"
  }
  ```

---

### GET /api/v1/analysis/publication/{publication_id}

Get publication status by ID

**Parameters:**

- `publication_id`: string (path)

**Responses:**

- `200`: Publication status retrieved successfully
  ```json
  {
    "id": "string",
    "title": "string",
    "type": "string",
    "format": "string",
    "status": "string (processing, completed, error)",
    "timestamp": "string (ISO format)",
    "download_url": "string (if completed)"
  }
  ```
- `404`: Publication not found

---

### GET /api/v1/analysis/publication/download/{publication_id}

Download publication file

**Parameters:**

- `publication_id`: string (path)

**Responses:**

- `200`: Publication file
  ```json
  File download (binary)
  ```
- `404`: Publication not found or not ready

---

### POST /api/v1/decisions/analyze

Analyze surgical case for decision support

**Request Body:**

```json
{
  "case_id": "string",
  "analysis_type": "string (flot, precision, adci)",
  "include_rationale": "boolean (optional)"
}
```

**Responses:**

- `200`: Analysis results
  ```json
  {
    "case_id": "string",
    "analysis_type": "string",
    "timestamp": "string (ISO format)",
    "recommendations": "array",
    "confidence_score": "number",
    "protocol_adherence": "number (if applicable)",
    "rationale": "object (if requested)"
  }
  ```

---

### POST /api/v1/decisions/track

Track decision implementation and outcomes

**Request Body:**

```json
{
  "case_id": "string",
  "decision_id": "string",
  "implemented": "boolean",
  "implementation_details": "string (optional)",
  "outcomes": "object (optional)"
}
```

**Responses:**

- `200`: Decision tracking updated
  ```json
  {
    "case_id": "string",
    "decision_id": "string",
    "tracking_id": "string",
    "timestamp": "string (ISO format)"
  }
  ```

---

### GET /api/v1/decisions/history/{case_id}

Get decision history for a case

**Parameters:**

- `case_id`: string (path)

**Responses:**

- `200`: Decision history
  ```json
  {
    "case_id": "string",
    "decisions": "array of decision objects",
    "count": "integer"
  }
  ```
- `404`: Case not found

---

