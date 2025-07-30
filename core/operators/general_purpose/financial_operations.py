"""
Financial Operations Operator
Handles financial tracking, billing, and monetary transactions across all domains
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class FinancialOperationsOperator:
    """Financial operations manager for cross-domain monetary transactions"""
    
    def __init__(self):
        """Initialize financial operations operator"""
        self.transactions = {}
        self.accounts = {}
        self.billing_records = {}
        self.payment_methods = {}
        logger.info("Financial operations operator initialized")
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a financial transaction"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        transaction_id = core_ops.generate_operation_id("TXN")
        
        # Validate required fields
        required_fields = ["amount", "transaction_type", "currency"]
        validation = core_ops.validate_operation_data(transaction_data, required_fields)
        
        if not validation["is_valid"]:
            raise ValueError(f"Invalid transaction data: {validation['errors']}")
        
        transaction = {
            "transaction_id": transaction_id,
            "amount": Decimal(str(transaction_data["amount"])),
            "currency": transaction_data.get("currency", "USD"),
            "transaction_type": transaction_data["transaction_type"],  # debit, credit, transfer
            "category": transaction_data.get("category", "general"),
            "description": transaction_data.get("description", ""),
            "from_account": transaction_data.get("from_account"),
            "to_account": transaction_data.get("to_account"),
            "reference_id": transaction_data.get("reference_id"),  # Link to case, patient, etc.
            "reference_type": transaction_data.get("reference_type"),  # case, patient, service
            "payment_method": transaction_data.get("payment_method"),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "created_by": transaction_data.get("user_id"),
            "metadata": transaction_data.get("metadata", {})
        }
        
        self.transactions[transaction_id] = transaction
        
        # Log the operation
        core_ops.log_operation("financial_transaction", {
            "user_id": transaction_data.get("user_id"),
            "data": {"transaction_id": transaction_id, "amount": float(transaction["amount"])}
        })
        
        logger.info(f"Created transaction: {transaction_id} - {transaction['amount']} {transaction['currency']}")
        return transaction
    
    def process_payment(self, transaction_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment for a transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction = self.transactions[transaction_id]
        
        payment_record = {
            "payment_id": f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "transaction_id": transaction_id,
            "amount_paid": Decimal(str(payment_data.get("amount", transaction["amount"]))),
            "payment_method": payment_data.get("payment_method", "unknown"),
            "payment_gateway": payment_data.get("gateway"),
            "gateway_transaction_id": payment_data.get("gateway_txn_id"),
            "status": "completed",
            "processed_at": datetime.now().isoformat(),
            "processor_response": payment_data.get("response", {})
        }
        
        # Update transaction status
        transaction["status"] = "completed"
        transaction["completed_at"] = datetime.now().isoformat()
        transaction["payment_record"] = payment_record
        
        logger.info(f"Processed payment for transaction: {transaction_id}")
        return payment_record
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice for services"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        invoice_id = core_ops.generate_operation_id("INV")
        
        line_items = invoice_data.get("line_items", [])
        subtotal = sum(Decimal(str(item.get("amount", 0))) for item in line_items)
        tax_rate = Decimal(str(invoice_data.get("tax_rate", 0.0)))
        tax_amount = subtotal * (tax_rate / 100)
        total_amount = subtotal + tax_amount
        
        invoice = {
            "invoice_id": invoice_id,
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_id[-4:]}",
            "customer_id": invoice_data.get("customer_id"),
            "customer_info": invoice_data.get("customer_info", {}),
            "line_items": line_items,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "currency": invoice_data.get("currency", "USD"),
            "due_date": invoice_data.get("due_date"),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "created_by": invoice_data.get("user_id"),
            "reference_id": invoice_data.get("reference_id"),
            "reference_type": invoice_data.get("reference_type"),
            "notes": invoice_data.get("notes", "")
        }
        
        self.billing_records[invoice_id] = invoice
        
        logger.info(f"Created invoice: {invoice_id} - {total_amount} {invoice['currency']}")
        return invoice
    
    def calculate_revenue_metrics(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Calculate revenue metrics for a time period"""
        if time_period is None:
            time_period = timedelta(days=30)
        
        cutoff_date = datetime.now() - time_period
        
        period_transactions = []
        for transaction in self.transactions.values():
            transaction_date = datetime.fromisoformat(transaction["created_at"])
            if transaction_date >= cutoff_date and transaction["status"] == "completed":
                period_transactions.append(transaction)
        
        total_revenue = sum(
            transaction["amount"] for transaction in period_transactions
            if transaction["transaction_type"] == "credit"
        )
        
        total_expenses = sum(
            transaction["amount"] for transaction in period_transactions
            if transaction["transaction_type"] == "debit"
        )
        
        net_income = total_revenue - total_expenses
        
        # Revenue by category
        revenue_by_category = {}
        for transaction in period_transactions:
            if transaction["transaction_type"] == "credit":
                category = transaction.get("category", "uncategorized")
                revenue_by_category[category] = revenue_by_category.get(category, Decimal('0')) + transaction["amount"]
        
        return {
            "period_days": time_period.days,
            "total_revenue": float(total_revenue),
            "total_expenses": float(total_expenses),
            "net_income": float(net_income),
            "transaction_count": len(period_transactions),
            "revenue_by_category": {k: float(v) for k, v in revenue_by_category.items()},
            "calculated_at": datetime.now().isoformat()
        }
    
    def create_financial_report(self, report_type: str, period: timedelta) -> Dict[str, Any]:
        """Generate financial reports"""
        if report_type == "revenue":
            return self.calculate_revenue_metrics(period)
        elif report_type == "transactions":
            return self._generate_transaction_report(period)
        elif report_type == "outstanding_invoices":
            return self._generate_outstanding_invoices_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def _generate_transaction_report(self, period: timedelta) -> Dict[str, Any]:
        """Generate detailed transaction report"""
        cutoff_date = datetime.now() - period
        
        period_transactions = [
            transaction for transaction in self.transactions.values()
            if datetime.fromisoformat(transaction["created_at"]) >= cutoff_date
        ]
        
        return {
            "report_type": "transactions",
            "period_days": period.days,
            "total_transactions": len(period_transactions),
            "transactions": period_transactions,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_outstanding_invoices_report(self) -> Dict[str, Any]:
        """Generate report of outstanding invoices"""
        outstanding_invoices = [
            invoice for invoice in self.billing_records.values()
            if invoice["status"] == "pending"
        ]
        
        total_outstanding = sum(
            invoice["total_amount"] for invoice in outstanding_invoices
        )
        
        return {
            "report_type": "outstanding_invoices",
            "total_outstanding": float(total_outstanding),
            "invoice_count": len(outstanding_invoices),
            "invoices": outstanding_invoices,
            "generated_at": datetime.now().isoformat()
        }
