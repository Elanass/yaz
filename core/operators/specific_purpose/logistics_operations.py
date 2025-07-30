"""
Logistics Operations Manager
Handles equipment, supplies, scheduling, and resource management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class LogisticsOperationsOperator:
    """Operations manager for logistics domain"""
    
    def __init__(self):
        self.inventory = {}
        self.equipment_schedule = {}
        self.supply_orders = {}
        self._initialize_inventory()
        logger.info("Logistics operator initialized")
    
    def _initialize_inventory(self):
        """Initialize basic surgical inventory"""
        self.inventory = {
            "surgical_instruments": {"quantity": 50, "unit": "sets", "min_threshold": 10},
            "sutures": {"quantity": 200, "unit": "packages", "min_threshold": 50},
            "gastric_staplers": {"quantity": 25, "unit": "units", "min_threshold": 5},
            "anesthesia_supplies": {"quantity": 100, "unit": "units", "min_threshold": 20},
            "surgical_gowns": {"quantity": 150, "unit": "pieces", "min_threshold": 30}
        }
    
    def check_supply_availability(self, required_supplies: Dict[str, int]) -> Dict[str, Any]:
        """Check if required supplies are available"""
        availability = {"available": True, "shortages": [], "reservations": {}}
        
        for item, quantity in required_supplies.items():
            if item in self.inventory:
                available_qty = self.inventory[item]["quantity"]
                if available_qty >= quantity:
                    availability["reservations"][item] = quantity
                else:
                    availability["available"] = False
                    availability["shortages"].append({
                        "item": item,
                        "required": quantity,
                        "available": available_qty,
                        "shortage": quantity - available_qty
                    })
        
        return availability
    
    def reserve_supplies(self, case_id: str, supplies: Dict[str, int]) -> Dict[str, Any]:
        """Reserve supplies for a surgical case"""
        availability = self.check_supply_availability(supplies)
        
        if not availability["available"]:
            raise ValueError(f"Insufficient supplies: {availability['shortages']}")
        
        # Reserve supplies
        for item, quantity in supplies.items():
            if item in self.inventory:
                self.inventory[item]["quantity"] -= quantity
        
        reservation = {
            "case_id": case_id,
            "supplies": supplies,
            "reserved_at": datetime.now().isoformat(),
            "status": "reserved"
        }
        
        logger.info(f"Reserved supplies for case {case_id}")
        return reservation
    
    def schedule_equipment(self, equipment_type: str, start_time: datetime, duration_hours: int) -> Dict[str, Any]:
        """Schedule equipment for a procedure"""
        end_time = start_time + timedelta(hours=duration_hours)
        schedule_id = f"EQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        if equipment_type not in self.equipment_schedule:
            self.equipment_schedule[equipment_type] = []
        
        # Check for conflicts (simplified)
        conflicts = []
        for existing in self.equipment_schedule[equipment_type]:
            existing_start = datetime.fromisoformat(existing["start_time"])
            existing_end = datetime.fromisoformat(existing["end_time"])
            
            if (start_time < existing_end and end_time > existing_start):
                conflicts.append(existing)
        
        if conflicts:
            raise ValueError(f"Equipment {equipment_type} is already scheduled during this time")
        
        schedule = {
            "schedule_id": schedule_id,
            "equipment_type": equipment_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_hours": duration_hours,
            "status": "scheduled"
        }
        
        self.equipment_schedule[equipment_type].append(schedule)
        logger.info(f"Scheduled {equipment_type} for {duration_hours} hours starting {start_time}")
        
        return schedule
    
    def create_supply_order(self, items: Dict[str, int], supplier: str = "Medical Supply Co") -> Dict[str, Any]:
        """Create a supply order for low inventory items"""
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        order = {
            "order_id": order_id,
            "supplier": supplier,
            "items": items,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat()
        }
        
        self.supply_orders[order_id] = order
        logger.info(f"Created supply order {order_id} for {len(items)} items")
        
        return order
    
    def check_low_inventory(self) -> List[Dict[str, Any]]:
        """Check for items below minimum threshold"""
        low_items = []
        
        for item, details in self.inventory.items():
            if details["quantity"] <= details["min_threshold"]:
                low_items.append({
                    "item": item,
                    "current_quantity": details["quantity"],
                    "minimum_threshold": details["min_threshold"],
                    "recommended_order": details["min_threshold"] * 2
                })
        
        return low_items
