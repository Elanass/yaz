"""
Cohorts service for managing patient cohorts, clinical series, and research groups.

This service provides functionality for:
- Managing patient cohorts for clinical studies
- Organizing clinical cases into series
- Supporting research data aggregation
- Integration with ADCI framework for decision support
"""

from typing import List, Dict, Any, Optional
import datetime
import uuid
from pydantic import BaseModel, Field

from core.services.logger import get_logger
from core.services.ipfs_client import IPFSClient
from core.services.encryption import encrypt_data
from services.event_logger.service import event_logger, EventCategory, EventSeverity

logger = get_logger(__name__)


class CohortModel(BaseModel):
    """Patient cohort model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    inclusion_criteria: List[str] = []
    exclusion_criteria: List[str] = []
    patient_count: int = 0
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    created_by: str
    status: str = "active"  # active, completed, archived
    

class SeriesModel(BaseModel):
    """Clinical series model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    author: str
    series_type: str  # case_series, research_series, educational_series
    featured: bool = False
    image_url: Optional[str] = None
    cases_count: int = 0
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class EventModel(BaseModel):
    """Clinical event model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: str  # conference, workshop, seminar, surgery
    date: datetime.datetime
    location: str
    capacity: Optional[int] = None
    registered_count: int = 0
    image_url: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class CohortsService:
    """Service for managing cohorts, series, and events."""
    
    def __init__(self):
        self.ipfs_client = IPFSClient()
    
    async def get_featured_series(self, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Get featured clinical series."""
        try:
            # Mock data for now - replace with actual database queries
            series_data = [
                {
                    "id": "series_1",
                    "title": "Advanced Gastric Cancer Management",
                    "subtitle": "Comprehensive surgical approaches and ADCI integration",
                    "description": "Latest techniques in gastric oncology surgery with decision support framework",
                    "image_url": "/static/images/gastric-series-1.jpg",
                    "type": "series",
                    "date": datetime.datetime.now() - datetime.timedelta(days=2),
                    "author": "Dr. Smith et al.",
                    "cases_count": 45,
                    "featured": True
                },
                {
                    "id": "series_2", 
                    "title": "FLOT Protocol Implementation",
                    "subtitle": "Perioperative chemotherapy guidelines",
                    "description": "Evidence-based FLOT protocol for gastric cancer with real-world outcomes",
                    "image_url": "/static/images/flot-series.jpg",
                    "type": "series",
                    "date": datetime.datetime.now() - datetime.timedelta(days=5),
                    "author": "European Oncology Group",
                    "cases_count": 127,
                    "featured": True
                },
                {
                    "id": "series_3",
                    "title": "Minimally Invasive Gastric Surgery",
                    "subtitle": "Laparoscopic and robotic approaches",
                    "description": "Comparison of surgical techniques in gastric cancer treatment",
                    "image_url": "/static/images/minimally-invasive.jpg",
                    "type": "series",
                    "date": datetime.datetime.now() - datetime.timedelta(days=10),
                    "author": "Dr. Chen & Team",
                    "cases_count": 78,
                    "featured": True
                }
            ]
            
            await event_logger.log_event(
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.INFO,
                message=f"Featured series retrieved: {len(series_data)} items",
                metadata={"limit": limit, "offset": offset}
            )
            
            return series_data[offset:offset+limit]
            
        except Exception as e:
            logger.error(f"Error fetching featured series: {str(e)}")
            await event_logger.log_event(
                category=EventCategory.SYSTEM_ERROR,
                severity=EventSeverity.ERROR,
                message=f"Featured series fetch error: {str(e)}",
                metadata={"error": str(e)}
            )
            return []
    
    async def get_upcoming_events(self, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Get upcoming clinical events."""
        try:
            events_data = [
                {
                    "id": "event_1",
                    "title": "Gastric Surgery Symposium 2025",
                    "subtitle": "International conference on gastric oncology",
                    "description": "Latest advances in gastric cancer surgery and ADCI framework applications",
                    "image_url": "/static/images/symposium-2025.jpg",
                    "type": "event",
                    "date": datetime.datetime.now() + datetime.timedelta(days=30),
                    "location": "Medical Center",
                    "capacity": 200,
                    "registered_count": 145
                },
                {
                    "id": "event_2",
                    "title": "ADCI Framework Workshop",
                    "subtitle": "Hands-on decision support training",
                    "description": "Learn to use the ADCI framework effectively in clinical practice",
                    "image_url": "/static/images/adci-workshop.jpg",
                    "type": "event",
                    "date": datetime.datetime.now() + datetime.timedelta(days=15),
                    "location": "Online",
                    "capacity": 100,
                    "registered_count": 67
                },
                {
                    "id": "event_3",
                    "title": "Multidisciplinary Gastric Cancer Board",
                    "subtitle": "Weekly case discussion",
                    "description": "Review complex gastric cancer cases with multidisciplinary team",
                    "image_url": "/static/images/tumor-board.jpg",
                    "type": "event",
                    "date": datetime.datetime.now() + datetime.timedelta(days=7),
                    "location": "Conference Room A",
                    "capacity": 25,
                    "registered_count": 18
                }
            ]
            
            await event_logger.log_event(
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.INFO,
                message=f"Upcoming events retrieved: {len(events_data)} items",
                metadata={"limit": limit, "offset": offset}
            )
            
            return events_data[offset:offset+limit]
            
        except Exception as e:
            logger.error(f"Error fetching upcoming events: {str(e)}")
            await event_logger.log_event(
                category=EventCategory.SYSTEM_ERROR,
                severity=EventSeverity.ERROR,
                message=f"Upcoming events fetch error: {str(e)}",
                metadata={"error": str(e)}
            )
            return []
    
    async def get_journal_articles(self, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Get latest journal articles."""
        try:
            articles_data = [
                {
                    "id": "article_1",
                    "title": "ADCI Framework Validation in Gastric Cancer: A Multi-Center Study",
                    "author": "Dr. Johnson et al.",
                    "abstract": "Comprehensive validation of the Adaptive Decision Confidence Index framework in gastric cancer surgical decision-making across multiple medical centers.",
                    "description": "Multi-center validation study of ADCI framework",
                    "journal": "Journal of Gastric Oncology",
                    "published_date": datetime.datetime.now() - datetime.timedelta(days=7),
                    "impact_factor": 8.5,
                    "image_url": "/static/images/adci-validation.jpg",
                    "type": "journal"
                },
                {
                    "id": "article_2",
                    "title": "Outcomes of FLOT Protocol in Locally Advanced Gastric Cancer",
                    "author": "Dr. Mueller et al.",
                    "abstract": "Long-term outcomes and survival analysis of patients treated with FLOT protocol for locally advanced gastric adenocarcinoma.",
                    "description": "FLOT protocol outcomes analysis",
                    "journal": "European Journal of Oncology",
                    "published_date": datetime.datetime.now() - datetime.timedelta(days=14),
                    "impact_factor": 7.2,
                    "image_url": "/static/images/flot-outcomes.jpg",
                    "type": "journal"
                },
                {
                    "id": "article_3",
                    "title": "AI-Assisted Decision Making in Gastric Surgery",
                    "author": "Dr. Wang et al.",
                    "abstract": "Integration of artificial intelligence and machine learning in gastric cancer surgical decision-making processes.",
                    "description": "AI integration in surgical decisions",
                    "journal": "AI in Medicine",
                    "published_date": datetime.datetime.now() - datetime.timedelta(days=21),
                    "impact_factor": 6.8,
                    "image_url": "/static/images/ai-surgery.jpg",
                    "type": "journal"
                }
            ]
            
            await event_logger.log_event(
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.INFO,
                message=f"Journal articles retrieved: {len(articles_data)} items",
                metadata={"limit": limit, "offset": offset}
            )
            
            return articles_data[offset:offset+limit]
            
        except Exception as e:
            logger.error(f"Error fetching journal articles: {str(e)}")
            await event_logger.log_event(
                category=EventCategory.SYSTEM_ERROR,
                severity=EventSeverity.ERROR,
                message=f"Journal articles fetch error: {str(e)}",
                metadata={"error": str(e)}
            )
            return []
    
    async def create_cohort(self, cohort_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new patient cohort."""
        try:
            cohort = CohortModel(
                name=cohort_data["name"],
                description=cohort_data.get("description"),
                inclusion_criteria=cohort_data.get("inclusion_criteria", []),
                exclusion_criteria=cohort_data.get("exclusion_criteria", []),
                created_by=created_by
            )
            
            # Store encrypted cohort data
            encrypted_data = await encrypt_data(cohort.dict())
            
            await event_logger.log_event(
                category=EventCategory.DATA_CREATION,
                severity=EventSeverity.INFO,
                message=f"Cohort created: {cohort.name}",
                metadata={"cohort_id": cohort.id, "created_by": created_by}
            )
            
            return cohort.dict()
            
        except Exception as e:
            logger.error(f"Error creating cohort: {str(e)}")
            await event_logger.log_event(
                category=EventCategory.SYSTEM_ERROR,
                severity=EventSeverity.ERROR,
                message=f"Cohort creation error: {str(e)}",
                metadata={"error": str(e)}
            )
            raise
    
    async def get_cohorts(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get cohorts accessible to user."""
        try:
            # Mock implementation - replace with actual database query
            cohorts = []
            
            await event_logger.log_event(
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.INFO,
                message=f"Cohorts retrieved for user {user_id}",
                metadata={"user_id": user_id, "count": len(cohorts)}
            )
            
            return cohorts
            
        except Exception as e:
            logger.error(f"Error fetching cohorts: {str(e)}")
            return []


# Global instance
cohorts_service = CohortsService()


# Helper functions for backward compatibility
async def get_featured_series(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get featured series - global function."""
    return await cohorts_service.get_featured_series(limit=limit, offset=offset)


async def get_upcoming_events(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get upcoming events - global function."""
    return await cohorts_service.get_upcoming_events(limit=limit, offset=offset)


async def get_journal_articles(limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Get journal articles - global function."""
    return await cohorts_service.get_journal_articles(limit=limit, offset=offset)
