from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from apps.surge.api.dependencies import get_async_session


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=dict)
async def upload_dataset(
    file: UploadFile = File(...), session: Session = Depends(get_async_session)
):
    # ...existing code...
    return {"filename": file.filename}
