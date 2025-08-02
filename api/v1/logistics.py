"""
Logistics API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

router = APIRouter()


class TransportType(str, Enum):
    ambulance = "ambulance"
    medical_transport = "medical_transport"
    private_vehicle = "private_vehicle"
    helicopter = "helicopter"


class ResourceType(str, Enum):
    equipment = "equipment"
    medication = "medication"
    supplies = "supplies"
    personnel = "personnel"


class PatientTransport(BaseModel):
    id: Optional[str] = None
    patient_id: str
    origin: str
    destination: str
    transport_type: TransportType
    scheduled_time: datetime
    estimated_duration_minutes: int
    status: str = "scheduled"
    notes: Optional[str] = None


class ResourceRequest(BaseModel):
    id: Optional[str] = None
    resource_type: ResourceType
    item_name: str
    quantity: int
    urgency: str = "routine"
    department: str
    requested_by: str
    needed_by: datetime
    status: str = "pending"


class SupplyInventory(BaseModel):
    id: Optional[str] = None
    item_name: str
    category: str
    current_stock: int
    minimum_threshold: int
    unit_cost: float
    supplier: str
    last_restocked: date


class StaffSchedule(BaseModel):
    id: Optional[str] = None
    staff_id: str
    name: str
    role: str
    department: str
    shift_start: datetime
    shift_end: datetime
    status: str = "scheduled"


@router.get("/")
async def logistics_root():
    """Logistics API root"""
    return {
        "message": "Logistics Management API",
        "version": "1.0.0",
        "endpoints": {
            "transport": "/api/v1/logistics/transport",
            "resources": "/api/v1/logistics/resources", 
            "inventory": "/api/v1/logistics/inventory",
            "staff": "/api/v1/logistics/staff",
            "supply-chain": "/api/v1/logistics/supply-chain"
        }
    }


@router.get("/transport")
async def get_patient_transports(status: Optional[str] = None):
    """Get patient transport requests"""
    # Mock data
    transports = [
        {
            "id": "trans_001",
            "patient_id": "pat_001",
            "origin": "Emergency Room",
            "destination": "Operating Room 3",
            "transport_type": "medical_transport",
            "scheduled_time": "2024-01-25T14:00:00Z",
            "estimated_duration_minutes": 15,
            "status": "completed"
        },
        {
            "id": "trans_002",
            "patient_id": "pat_002",
            "origin": "Home",
            "destination": "Hospital Main Entrance",
            "transport_type": "ambulance",
            "scheduled_time": "2024-01-25T16:30:00Z",
            "estimated_duration_minutes": 25,
            "status": "scheduled"
        }
    ]
    
    if status:
        transports = [t for t in transports if t["status"] == status]
    
    return {"transports": transports, "total": len(transports)}


@router.post("/transport")
async def schedule_patient_transport(transport: PatientTransport):
    """Schedule a new patient transport"""
    if not transport.id:
        transport.id = f"trans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Patient transport scheduled successfully",
        "transport": transport.dict()
    }


@router.get("/transport/{transport_id}")
async def get_patient_transport(transport_id: str):
    """Get specific patient transport by ID"""
    # Mock data - in real app, query database
    if transport_id == "trans_001":
        return {
            "id": "trans_001",
            "patient_id": "pat_001",
            "origin": "Emergency Room", 
            "destination": "Operating Room 3",
            "transport_type": "medical_transport",
            "scheduled_time": "2024-01-25T14:00:00Z",
            "estimated_duration_minutes": 15,
            "status": "completed",
            "actual_duration_minutes": 12
        }
    raise HTTPException(status_code=404, detail="Transport not found")


@router.put("/transport/{transport_id}/status")
async def update_transport_status(transport_id: str, status: str):
    """Update patient transport status"""
    valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    return {
        "message": f"Transport {transport_id} status updated to {status}",
        "transport_id": transport_id,
        "new_status": status,
        "updated_at": datetime.now()
    }


@router.get("/resources")
async def get_resource_requests(status: Optional[str] = None, urgency: Optional[str] = None):
    """Get resource requests"""
    # Mock data
    requests = [
        {
            "id": "req_001",
            "resource_type": "equipment",
            "item_name": "Laparoscopic Camera",
            "quantity": 1,
            "urgency": "urgent",
            "department": "Surgery",
            "requested_by": "Dr. Smith",
            "needed_by": "2024-01-25T08:00:00Z",
            "status": "approved"
        },
        {
            "id": "req_002",
            "resource_type": "medication",
            "item_name": "Propofol 10mg/ml",
            "quantity": 5,
            "urgency": "routine",
            "department": "Anesthesiology",
            "requested_by": "Dr. Johnson",
            "needed_by": "2024-01-26T10:00:00Z",
            "status": "pending"
        }
    ]
    
    filtered_requests = requests
    if status:
        filtered_requests = [r for r in filtered_requests if r["status"] == status]
    if urgency:
        filtered_requests = [r for r in filtered_requests if r["urgency"] == urgency]
    
    return {"requests": filtered_requests, "total": len(filtered_requests)}


@router.post("/resources")
async def create_resource_request(request: ResourceRequest):
    """Create a new resource request"""
    if not request.id:
        request.id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Resource request created successfully",
        "request": request.dict()
    }


@router.get("/resources/{request_id}")
async def get_resource_request(request_id: str):
    """Get specific resource request by ID"""
    # Mock data - in real app, query database
    if request_id == "req_001":
        return {
            "id": "req_001",
            "resource_type": "equipment",
            "item_name": "Laparoscopic Camera",
            "quantity": 1,
            "urgency": "urgent",
            "department": "Surgery",
            "requested_by": "Dr. Smith",
            "needed_by": "2024-01-25T08:00:00Z",
            "status": "approved",
            "approved_by": "Admin",
            "approved_at": "2024-01-24T16:30:00Z"
        }
    raise HTTPException(status_code=404, detail="Resource request not found")


@router.put("/resources/{request_id}/status")
async def update_resource_status(request_id: str, status: str):
    """Update resource request status"""
    valid_statuses = ["pending", "approved", "denied", "fulfilled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    return {
        "message": f"Resource request {request_id} status updated to {status}",
        "request_id": request_id,
        "new_status": status,
        "updated_at": datetime.now()
    }


@router.get("/inventory")
async def get_supply_inventory(category: Optional[str] = None, low_stock: bool = False):
    """Get supply inventory"""
    # Mock data
    inventory = [
        {
            "id": "inv_001",
            "item_name": "Surgical Gloves (Large)",
            "category": "PPE",
            "current_stock": 150,
            "minimum_threshold": 50,
            "unit_cost": 0.25,
            "supplier": "MedSupply Co",
            "last_restocked": "2024-01-20"
        },
        {
            "id": "inv_002", 
            "item_name": "Sterile Gauze Pads",
            "category": "Supplies",
            "current_stock": 25,
            "minimum_threshold": 100,
            "unit_cost": 0.15,
            "supplier": "HealthCare Supplies Inc",
            "last_restocked": "2024-01-15"
        },
        {
            "id": "inv_003",
            "item_name": "Propofol 10mg/ml",
            "category": "Medications",
            "current_stock": 75,
            "minimum_threshold": 30,
            "unit_cost": 12.50,
            "supplier": "PharmaCorp",
            "last_restocked": "2024-01-22"
        }
    ]
    
    filtered_inventory = inventory
    if category:
        filtered_inventory = [i for i in filtered_inventory if i["category"].lower() == category.lower()]
    if low_stock:
        filtered_inventory = [i for i in filtered_inventory if i["current_stock"] <= i["minimum_threshold"]]
    
    return {"inventory": filtered_inventory, "total": len(filtered_inventory)}


@router.post("/inventory")
async def add_inventory_item(item: SupplyInventory):
    """Add a new inventory item"""
    if not item.id:
        item.id = f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Inventory item added successfully",
        "item": item.dict()
    }


@router.put("/inventory/{item_id}/restock")
async def restock_inventory_item(item_id: str, quantity: int):
    """Restock an inventory item"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    return {
        "message": f"Item {item_id} restocked with {quantity} units",
        "item_id": item_id,
        "quantity_added": quantity,
        "restocked_at": datetime.now()
    }


@router.get("/staff")
async def get_staff_schedule(department: Optional[str] = None, date: Optional[str] = None):
    """Get staff schedule"""
    # Mock data
    schedules = [
        {
            "id": "sched_001",
            "staff_id": "staff_001",
            "name": "Dr. Smith",
            "role": "Surgeon",
            "department": "Surgery",
            "shift_start": "2024-01-25T07:00:00Z",
            "shift_end": "2024-01-25T19:00:00Z",
            "status": "scheduled"
        },
        {
            "id": "sched_002",
            "staff_id": "staff_002", 
            "name": "Nurse Johnson",
            "role": "Nurse",
            "department": "Surgery",
            "shift_start": "2024-01-25T06:00:00Z",
            "shift_end": "2024-01-25T18:00:00Z",
            "status": "active"
        },
        {
            "id": "sched_003",
            "staff_id": "staff_003",
            "name": "Dr. Wilson",
            "role": "Anesthesiologist", 
            "department": "Anesthesiology",
            "shift_start": "2024-01-25T08:00:00Z",
            "shift_end": "2024-01-25T16:00:00Z",
            "status": "scheduled"
        }
    ]
    
    filtered_schedules = schedules
    if department:
        filtered_schedules = [s for s in filtered_schedules if s["department"].lower() == department.lower()]
    
    return {"schedules": filtered_schedules, "total": len(filtered_schedules)}


@router.post("/staff")
async def create_staff_schedule(schedule: StaffSchedule):
    """Create a new staff schedule"""
    if not schedule.id:
        schedule.id = f"sched_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Staff schedule created successfully",
        "schedule": schedule.dict()
    }


@router.get("/statistics")
async def get_logistics_statistics():
    """Get logistics-related statistics"""
    return {
        "transports": {
            "total_today": 15,
            "completed": 12,
            "scheduled": 3,
            "average_duration_minutes": 18
        },
        "resources": {
            "pending_requests": 8,
            "approved_today": 25,
            "urgent_requests": 3
        },
        "inventory": {
            "total_items": 150,
            "low_stock_items": 12,
            "out_of_stock_items": 2,
            "total_inventory_value": 45000.00
        },
        "staff": {
            "total_staff_on_duty": 45,
            "surgery_department": 12,
            "emergency_department": 8,
            "icu": 10
        }
    }


@router.get("/supply-chain")
async def get_supply_chain():
    """Get supply chain management dashboard - for sidebar link"""
    supply_chain = {
        "suppliers": [
            {"name": "MedEquip Inc", "status": "active", "reliability": 95, "orders": 12},
            {"name": "SurgicalSupply Co", "status": "active", "reliability": 88, "orders": 8},
            {"name": "BioMed Solutions", "status": "pending", "reliability": 92, "orders": 5}
        ],
        "orders": {
            "pending": 15,
            "in_transit": 8,
            "delivered": 45,
            "overdue": 2
        },
        "critical_items": [
            {"item": "Surgical Gloves", "stock": 150, "minimum": 200, "status": "low"},
            {"item": "Anesthesia Masks", "stock": 25, "minimum": 50, "status": "critical"},
            {"item": "Gauze Pads", "stock": 85, "minimum": 100, "status": "low"}
        ],
        "delivery_performance": {
            "on_time_percentage": 92.5,
            "average_delay_days": 1.2,
            "last_30_days": {
                "total_deliveries": 38,
                "on_time": 35,
                "delayed": 3
            }
        }
    }
    return supply_chain
