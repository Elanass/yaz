"""
General Purpose Operations Manager
Handles financial tracking, equity management, branding, and communications
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class GeneralOperator:
    """General purpose operations manager"""
    
    def __init__(self):
        self.financial_records = {}
        self.equity_positions = {}
        self.communication_log = {}
        self.brand_assets = {}
        logger.info("General operator initialized")
    
    def track_financial_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track financial transactions"""
        transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        transaction = {
            "transaction_id": transaction_id,
            "type": transaction_data.get("type", "revenue"),  # revenue, expense, investment
            "amount": transaction_data.get("amount", 0.0),
            "category": transaction_data.get("category", "operations"),
            "description": transaction_data.get("description", ""),
            "related_case_id": transaction_data.get("case_id"),
            "timestamp": datetime.now().isoformat(),
            "status": "recorded"
        }
        
        self.financial_records[transaction_id] = transaction
        logger.info(f"Recorded financial transaction: {transaction_id}")
        
        return transaction
    
    def calculate_case_profitability(self, case_id: str) -> Dict[str, Any]:
        """Calculate profitability for a specific case"""
        revenues = []
        expenses = []
        
        # Find all transactions related to this case
        for txn in self.financial_records.values():
            if txn.get("related_case_id") == case_id:
                if txn["type"] == "revenue":
                    revenues.append(txn["amount"])
                elif txn["type"] == "expense":
                    expenses.append(txn["amount"])
        
        total_revenue = sum(revenues)
        total_expenses = sum(expenses)
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "case_id": case_id,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin_percent": round(profit_margin, 2),
            "calculated_at": datetime.now().isoformat()
        }
    
    def manage_equity_position(self, stakeholder: str, shares: int, action: str = "allocate") -> Dict[str, Any]:
        """Manage equity positions for stakeholders"""
        if stakeholder not in self.equity_positions:
            self.equity_positions[stakeholder] = {"shares": 0, "history": []}
        
        if action == "allocate":
            self.equity_positions[stakeholder]["shares"] += shares
        elif action == "transfer":
            self.equity_positions[stakeholder]["shares"] -= shares
        
        equity_record = {
            "stakeholder": stakeholder,
            "action": action,
            "shares": shares,
            "new_total": self.equity_positions[stakeholder]["shares"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.equity_positions[stakeholder]["history"].append(equity_record)
        logger.info(f"Updated equity for {stakeholder}: {action} {shares} shares")
        
        return equity_record
    
    def log_communication(self, communication_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Log internal/external communications"""
        comm_id = f"COMM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        communication = {
            "communication_id": comm_id,
            "type": communication_type,  # internal, external, marketing, regulatory
            "channel": details.get("channel", "email"),  # email, phone, meeting, social
            "recipients": details.get("recipients", []),
            "subject": details.get("subject", ""),
            "content": details.get("content", ""),
            "sender": details.get("sender", "system"),
            "timestamp": datetime.now().isoformat(),
            "priority": details.get("priority", "normal")
        }
        
        self.communication_log[comm_id] = communication
        logger.info(f"Logged {communication_type} communication: {comm_id}")
        
        return communication
    
    def manage_brand_asset(self, asset_type: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage brand assets and marketing materials"""
        asset_id = f"BRAND-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        brand_asset = {
            "asset_id": asset_id,
            "type": asset_type,  # logo, template, guidelines, campaign
            "name": asset_data.get("name", ""),
            "description": asset_data.get("description", ""),
            "file_path": asset_data.get("file_path", ""),
            "version": asset_data.get("version", "1.0"),
            "status": asset_data.get("status", "active"),
            "created_at": datetime.now().isoformat(),
            "tags": asset_data.get("tags", [])
        }
        
        self.brand_assets[asset_id] = brand_asset
        logger.info(f"Registered brand asset: {asset_id}")
        
        return brand_asset
    
    def generate_financial_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate financial report for a date range"""
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        relevant_transactions = []
        for txn in self.financial_records.values():
            txn_date = datetime.fromisoformat(txn["timestamp"])
            if start_dt <= txn_date <= end_dt:
                relevant_transactions.append(txn)
        
        revenue_by_category = {}
        expense_by_category = {}
        
        total_revenue = 0
        total_expenses = 0
        
        for txn in relevant_transactions:
            category = txn["category"]
            amount = txn["amount"]
            
            if txn["type"] == "revenue":
                total_revenue += amount
                revenue_by_category[category] = revenue_by_category.get(category, 0) + amount
            elif txn["type"] == "expense":
                total_expenses += amount
                expense_by_category[category] = expense_by_category.get(category, 0) + amount
        
        return {
            "period": {"start": start_date, "end": end_date},
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": total_revenue - total_expenses,
            "revenue_by_category": revenue_by_category,
            "expense_by_category": expense_by_category,
            "transaction_count": len(relevant_transactions),
            "generated_at": datetime.now().isoformat()
        }
