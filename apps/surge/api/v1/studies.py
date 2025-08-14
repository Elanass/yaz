from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.surge.api.dependencies import get_async_session


router = APIRouter(prefix="/studies", tags=["studies"])


@router.get("/", response_model=list)
async def list_studies(session: Session = Depends(get_async_session)):
    # ...existing code...
    return []


@router.post("/", response_model=dict)
async def create_study(study: dict, session: Session = Depends(get_async_session)):
    # ...existing code...
    return {}
