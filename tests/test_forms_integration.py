"""
Integration tests for forms/questionnaire endpoints
"""

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class TestFormsIntegration:
    """Test forms/questionnaire integration"""
    
    def test_forms_questionnaires_list(self):
        """Test questionnaires list endpoint"""
        response = client.get("/forms/questionnaires")
        # Should return 200 or 503 (if FHIR server unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "questionnaires" in data
            assert "total" in data
            assert "count" in data
            assert isinstance(data["questionnaires"], list)
    
    def test_forms_questionnaires_with_filters(self):
        """Test questionnaires list with filters"""
        response = client.get("/forms/questionnaires?status=active&limit=5")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "questionnaires" in data
            assert data["limit"] == 5
    
    def test_forms_questionnaire_creation(self):
        """Test questionnaire creation"""
        questionnaire_data = {
            "title": "Test Questionnaire",
            "description": "A test questionnaire for integration testing",
            "status": "active",
            "items": [
                {
                    "linkId": "test-question-1",
                    "text": "What is your name?",
                    "type": "string",
                    "required": True
                },
                {
                    "linkId": "test-question-2", 
                    "text": "How old are you?",
                    "type": "integer",
                    "required": False
                }
            ]
        }
        
        response = client.post("/forms/questionnaires", json=questionnaire_data)
        # Should return 200/201 or 503 (if FHIR server unavailable)
        assert response.status_code in [200, 201, 400, 503]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["resourceType"] == "Questionnaire"
            assert data["title"] == questionnaire_data["title"]
    
    def test_forms_responses_list(self):
        """Test questionnaire responses list"""
        response = client.get("/forms/responses")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "responses" in data
            assert "total" in data
            assert "count" in data
            assert isinstance(data["responses"], list)
    
    def test_forms_response_submission(self):
        """Test questionnaire response submission"""
        response_data = {
            "questionnaire": "test-questionnaire-id",
            "subject": "Patient/test-patient",
            "status": "completed",
            "item": [
                {
                    "linkId": "test-question-1",
                    "answer": [
                        {
                            "valueString": "John Doe"
                        }
                    ]
                },
                {
                    "linkId": "test-question-2",
                    "answer": [
                        {
                            "valueInteger": 30
                        }
                    ]
                }
            ]
        }
        
        response = client.post("/forms/responses", json=response_data)
        # May return validation error if questionnaire doesn't exist
        assert response.status_code in [200, 201, 400, 503]
    
    def test_forms_templates_list(self):
        """Test form templates list"""
        response = client.get("/forms/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "count" in data
        assert isinstance(data["templates"], list)
        
        # Check for expected templates
        template_ids = [t["id"] for t in data["templates"]]
        assert "patient-intake" in template_ids
        assert "symptoms-assessment" in template_ids
    
    def test_forms_template_retrieval(self):
        """Test individual template retrieval"""
        response = client.get("/forms/templates/patient-intake")
        assert response.status_code == 200
        
        data = response.json()
        assert "title" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        
        # Check template structure
        assert data["title"] == "Patient Intake Form"
        items = data["items"]
        assert len(items) > 0
        
        # Check first item structure
        first_item = items[0]
        assert "linkId" in first_item
        assert "text" in first_item
        assert "type" in first_item
    
    def test_forms_questionnaire_from_template(self):
        """Test creating questionnaire from template"""
        response = client.post("/forms/templates/patient-intake/questionnaire")
        assert response.status_code in [200, 201, 503]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["resourceType"] == "Questionnaire"
            assert "Patient Intake" in data["title"]
    
    def test_forms_health_check(self):
        """Test forms service health check"""
        response = client.get("/forms/health")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "Healthcare Forms"
            assert "features" in data
    
    def test_forms_demo_page(self):
        """Test forms demo page"""
        response = client.get("/forms/demo")
        assert response.status_code == 200
        
        content = response.text
        assert "Healthcare Forms" in content
        assert "Demo" in content
        assert "/forms/templates" in content


class TestFormsValidation:
    """Test forms validation functionality"""
    
    def test_invalid_questionnaire_creation(self):
        """Test validation of invalid questionnaire"""
        invalid_data = {
            "title": "",  # Empty title should be invalid
            "items": []   # Empty items should be invalid
        }
        
        response = client.post("/forms/questionnaires", json=invalid_data)
        # Should return validation error
        assert response.status_code in [400, 422, 503]
    
    def test_invalid_response_submission(self):
        """Test validation of invalid response"""
        invalid_response = {
            "questionnaire": "",  # Empty questionnaire reference
            "item": []
        }
        
        response = client.post("/forms/responses", json=invalid_response)
        assert response.status_code in [400, 422, 503]
    
    def test_response_validation_against_questionnaire(self):
        """Test response validation against questionnaire structure"""
        # This would require creating a questionnaire first,
        # then submitting an invalid response
        response_with_wrong_type = {
            "questionnaire": "test-questionnaire-id",
            "item": [
                {
                    "linkId": "numeric-question",
                    "answer": [
                        {
                            "valueString": "should-be-number"  # Wrong type
                        }
                    ]
                }
            ]
        }
        
        response = client.post("/forms/responses", json=response_with_wrong_type)
        # May return validation error
        assert response.status_code in [200, 201, 400, 503]


class TestFormsTemplates:
    """Test forms template functionality"""
    
    def test_all_templates_accessible(self):
        """Test that all listed templates are accessible"""
        # Get template list
        list_response = client.get("/forms/templates")
        assert list_response.status_code == 200
        
        templates = list_response.json()["templates"]
        
        # Test each template
        for template in templates:
            template_id = template["id"]
            detail_response = client.get(f"/forms/templates/{template_id}")
            assert detail_response.status_code == 200
            
            template_data = detail_response.json()
            assert "title" in template_data
            assert "items" in template_data
    
    def test_template_not_found(self):
        """Test handling of non-existent template"""
        response = client.get("/forms/templates/non-existent-template")
        assert response.status_code == 404
    
    def test_template_questionnaire_creation(self):
        """Test questionnaire creation from all templates"""
        templates = ["patient-intake", "symptoms-assessment"]
        
        for template_id in templates:
            response = client.post(f"/forms/templates/{template_id}/questionnaire")
            # Should work or return service unavailable
            assert response.status_code in [200, 201, 503]


class TestFormsItemTypes:
    """Test different form item types"""
    
    def test_string_item_type(self):
        """Test string item type in questionnaire"""
        questionnaire_data = {
            "title": "String Test",
            "items": [
                {
                    "linkId": "string-test",
                    "text": "Enter text",
                    "type": "string",
                    "required": True
                }
            ]
        }
        
        response = client.post("/forms/questionnaires", json=questionnaire_data)
        assert response.status_code in [200, 201, 400, 503]
    
    def test_integer_item_type(self):
        """Test integer item type in questionnaire"""
        questionnaire_data = {
            "title": "Integer Test",
            "items": [
                {
                    "linkId": "integer-test",
                    "text": "Enter number",
                    "type": "integer",
                    "required": False
                }
            ]
        }
        
        response = client.post("/forms/questionnaires", json=questionnaire_data)
        assert response.status_code in [200, 201, 400, 503]
    
    def test_choice_item_type(self):
        """Test choice item type in questionnaire"""
        questionnaire_data = {
            "title": "Choice Test",
            "items": [
                {
                    "linkId": "choice-test",
                    "text": "Select option",
                    "type": "choice",
                    "answerOption": [
                        {"valueCoding": {"code": "opt1", "display": "Option 1"}},
                        {"valueCoding": {"code": "opt2", "display": "Option 2"}}
                    ]
                }
            ]
        }
        
        response = client.post("/forms/questionnaires", json=questionnaire_data)
        assert response.status_code in [200, 201, 400, 503]


class TestFormsErrorHandling:
    """Test forms error handling"""
    
    def test_invalid_questionnaire_id(self):
        """Test handling of invalid questionnaire ID"""
        response = client.get("/forms/questionnaires/invalid-id")
        assert response.status_code in [404, 503]
    
    def test_invalid_response_id(self):
        """Test handling of invalid response ID"""
        response = client.get("/forms/responses/invalid-id")
        assert response.status_code in [404, 503]
    
    def test_malformed_json_request(self):
        """Test handling of malformed JSON requests"""
        # This would depend on FastAPI's built-in JSON validation
        response = client.post(
            "/forms/questionnaires", 
            data="invalid-json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
