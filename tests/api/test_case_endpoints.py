from fastapi.testclient import TestClient

from apps.surge.main import app


client = TestClient(app)


class TestCaseEndpoints:
    def test_create_case(self):
        """Test case creation endpoint."""
        response = client.post(
            "/api/v1/cases/cases",
            json={
                "patient_id": "P001",
                "procedure_type": "Appendectomy",
                "status": "Planned",
                "notes": "Patient is ready for surgery",
            },
        )
        assert response.status_code == 200
        assert response.json()["patient_id"] == "P001"
        assert response.json()["procedure_type"] == "Appendectomy"

    def test_list_cases(self):
        """Test case listing endpoint."""
        response = client.get("/api/v1/cases/cases")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_case(self):
        """Test get case by ID endpoint."""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/cases",
            json={
                "patient_id": "P002",
                "surgery_type": "Cholecystectomy",
                "status": "Active",
                "pre_op_notes": "Pre-op completed",
                "post_op_notes": "",
            },
        )
        case_id = create_response.json()["id"]

        # Get the case
        response = client.get(f"/api/v1/cases/cases/{case_id}")
        assert response.status_code == 200
        assert response.json()["patient_id"] == "P002"

    def test_update_case(self):
        """Test case update endpoint."""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/cases",
            json={
                "patient_id": "P003",
                "surgery_type": "Hernia Repair",
                "status": "Planned",
                "pre_op_notes": "Initial notes",
                "post_op_notes": "",
            },
        )
        case_id = create_response.json()["id"]

        # Update the case
        response = client.put(
            f"/api/v1/cases/cases/{case_id}",
            json={
                "patient_id": "P003",
                "surgery_type": "Hernia Repair",
                "status": "Completed",
                "pre_op_notes": "Initial notes",
                "post_op_notes": "Surgery completed successfully",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Completed"

    def test_delete_case(self):
        """Test case deletion endpoint."""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/cases",
            json={
                "patient_id": "P004",
                "surgery_type": "Gallbladder Surgery",
                "status": "Planned",
                "pre_op_notes": "To be deleted",
                "post_op_notes": "",
            },
        )
        case_id = create_response.json()["id"]

        # Delete the case
        response = client.delete(f"/api/v1/cases/cases/{case_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["detail"]
