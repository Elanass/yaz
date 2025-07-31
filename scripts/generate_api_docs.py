#!/usr/bin/env python3
"""
Generate API documentation for new endpoints
"""

import os
import json
from datetime import datetime

# New API endpoints documentation
API_DOCS = {
    "title": "Decision Precision in Surgery API - Documentation Update",
    "version": "1.1.0",
    "updated": datetime.now().strftime("%Y-%m-%d"),
    "new_endpoints": [
        {
            "path": "/api/v1/analysis/insights/generate",
            "method": "POST",
            "description": "Generate insights from cohort data",
            "request_body": {
                "cohort_id": "string",
                "insight_types": ["basic_statistics", "flot_adherence", "albumin_trends", "survival_analysis", "multivariate_analysis", "decision_impact"],
                "notify_email": "string (optional)"
            },
            "responses": {
                "200": {
                    "description": "Insights generated successfully",
                    "content": {
                        "id": "string",
                        "timestamp": "string (ISO format)",
                        "cohort_size": "integer",
                        "results": "object with insight data"
                    }
                }
            }
        },
        {
            "path": "/api/v1/analysis/insights/{insight_id}",
            "method": "GET",
            "description": "Get generated insights by ID",
            "parameters": {
                "insight_id": "string (path)"
            },
            "responses": {
                "200": {
                    "description": "Insights retrieved successfully",
                    "content": "same as POST response"
                },
                "404": {
                    "description": "Insights not found"
                }
            }
        },
        {
            "path": "/api/v1/analysis/publication/prepare",
            "method": "POST",
            "description": "Prepare publication from cohort data",
            "request_body": {
                "cohort_id": "string",
                "publication_type": "string (memoir, article, infographic)",
                "output_format": "string (pdf, docx, html)",
                "title": "string",
                "authors": ["string"],
                "notify_email": "string (optional)"
            },
            "responses": {
                "200": {
                    "description": "Publication preparation started",
                    "content": {
                        "id": "string",
                        "title": "string",
                        "type": "string",
                        "format": "string",
                        "status": "string (processing)",
                        "timestamp": "string (ISO format)"
                    }
                }
            }
        },
        {
            "path": "/api/v1/analysis/publication/{publication_id}",
            "method": "GET",
            "description": "Get publication status by ID",
            "parameters": {
                "publication_id": "string (path)"
            },
            "responses": {
                "200": {
                    "description": "Publication status retrieved successfully",
                    "content": {
                        "id": "string",
                        "title": "string",
                        "type": "string",
                        "format": "string",
                        "status": "string (processing, completed, error)",
                        "timestamp": "string (ISO format)",
                        "download_url": "string (if completed)"
                    }
                },
                "404": {
                    "description": "Publication not found"
                }
            }
        },
        {
            "path": "/api/v1/analysis/publication/download/{publication_id}",
            "method": "GET",
            "description": "Download publication file",
            "parameters": {
                "publication_id": "string (path)"
            },
            "responses": {
                "200": {
                    "description": "Publication file",
                    "content": "File download (binary)"
                },
                "404": {
                    "description": "Publication not found or not ready"
                }
            }
        },
        {
            "path": "/api/v1/decisions/analyze",
            "method": "POST",
            "description": "Analyze surgical case for decision support",
            "request_body": {
                "case_id": "string",
                "analysis_type": "string (flot, precision, adci)",
                "include_rationale": "boolean (optional)"
            },
            "responses": {
                "200": {
                    "description": "Analysis results",
                    "content": {
                        "case_id": "string",
                        "analysis_type": "string",
                        "timestamp": "string (ISO format)",
                        "recommendations": "array",
                        "confidence_score": "number",
                        "protocol_adherence": "number (if applicable)",
                        "rationale": "object (if requested)"
                    }
                }
            }
        },
        {
            "path": "/api/v1/decisions/track",
            "method": "POST",
            "description": "Track decision implementation and outcomes",
            "request_body": {
                "case_id": "string",
                "decision_id": "string",
                "implemented": "boolean",
                "implementation_details": "string (optional)",
                "outcomes": "object (optional)"
            },
            "responses": {
                "200": {
                    "description": "Decision tracking updated",
                    "content": {
                        "case_id": "string",
                        "decision_id": "string",
                        "tracking_id": "string",
                        "timestamp": "string (ISO format)"
                    }
                }
            }
        },
        {
            "path": "/api/v1/decisions/history/{case_id}",
            "method": "GET",
            "description": "Get decision history for a case",
            "parameters": {
                "case_id": "string (path)"
            },
            "responses": {
                "200": {
                    "description": "Decision history",
                    "content": {
                        "case_id": "string",
                        "decisions": "array of decision objects",
                        "count": "integer"
                    }
                },
                "404": {
                    "description": "Case not found"
                }
            }
        }
    ]
}

# Generate documentation file
output_path = os.path.join("docs", "API_DOCUMENTATION.md")

with open(output_path, "w") as f:
    f.write(f"# {API_DOCS['title']}\n\n")
    f.write(f"**Version:** {API_DOCS['version']}  \n")
    f.write(f"**Updated:** {API_DOCS['updated']}  \n\n")
    
    f.write("## New Endpoints\n\n")
    
    for endpoint in API_DOCS["new_endpoints"]:
        f.write(f"### {endpoint['method']} {endpoint['path']}\n\n")
        f.write(f"{endpoint['description']}\n\n")
        
        if endpoint.get("parameters"):
            f.write("**Parameters:**\n\n")
            for name, desc in endpoint["parameters"].items():
                f.write(f"- `{name}`: {desc}\n")
            f.write("\n")
        
        if endpoint.get("request_body"):
            f.write("**Request Body:**\n\n")
            f.write("```json\n")
            f.write(json.dumps(endpoint["request_body"], indent=2))
            f.write("\n```\n\n")
        
        f.write("**Responses:**\n\n")
        for status, response in endpoint["responses"].items():
            f.write(f"- `{status}`: {response['description']}\n")
            if response.get("content"):
                f.write("  ```json\n  ")
                if isinstance(response["content"], str):
                    f.write(response["content"])
                else:
                    f.write(json.dumps(response["content"], indent=2).replace("\n", "\n  "))
                f.write("\n  ```\n")
        
        f.write("\n---\n\n")

print(f"API documentation generated at {output_path}")
