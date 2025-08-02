from fastapi.testclient import TestClient
import json
from pathlib import Path

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from main import app

client = TestClient(app)


def test_generate_insights_endpoint():
    """Integration test for insights generate endpoint"""
    payload = {
        "data": {"sample": "value"},
        "analysis_type": "prospective"
    }
    response = client.post("/api/v1/analysis/insights/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "analysis_id" in data
    assert "results" in data
    assert "metadata" in data
    assert data.get("reproducible") is True


def test_publication_prepare_and_download():
    """Integration test for publication prepare and download endpoints"""
    cohort_id = "test_cohort"
    # Prepare processed cohort data
    uploads_dir = Path("data/uploads") / cohort_id
    os.makedirs(uploads_dir, exist_ok=True)
    processed_file = uploads_dir / "processed_data.json"
    with open(processed_file, "w") as f:
        json.dump({"dummy": True}, f)

    payload = {
        "cohort_id": cohort_id,
        "publication_type": "memoir",
        "title": "Test Publication",
        "authors": ["Author A"],
        "template_id": None,
        "custom_fields": {}
    }
    response = client.post("/api/v1/analysis/publication/prepare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    pub_id = data.get("publication_id")
    download_url = data.get("download_url")

    # Stub out generated PDF for download
    pub_dir = Path("data/uploads/publications")
    os.makedirs(pub_dir, exist_ok=True)
    pdf_path = pub_dir / f"{pub_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4 stub PDF content")

    # Test download endpoint
    download_response = client.get(download_url)
    assert download_response.status_code == 200
    assert download_response.headers.get("content-type") == "application/pdf"
    assert download_response.content.startswith(b"%PDF")
