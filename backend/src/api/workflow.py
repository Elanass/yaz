from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/workflow", tags=["guided_workflow"])

@router.get("/step/{step_id}", response_class=HTMLResponse)
async def get_workflow_step(step_id: int):
    """Serve a specific step in the guided workflow."""
    try:
        steps = {
            1: {"title": "Step 1: Patient Information", "content": "Collect patient demographics and medical history."},
            2: {"title": "Step 2: Clinical Assessment", "content": "Record clinical findings and initial diagnosis."},
            3: {"title": "Step 3: Decision Support", "content": "Use the decision engine to recommend treatment options."}
        }

        step = steps.get(step_id)
        if not step:
            raise HTTPException(status_code=404, detail="Step not found")

        # Return HTML content for the step
        return f"""
        <h2>{step['title']}</h2>
        <p>{step['content']}</p>
        <button hx-get='/api/workflow/step/{step_id + 1}' hx-target='#workflow-container' hx-swap='innerHTML'>Next Step</button>
        """
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve workflow step: {str(e)}")
