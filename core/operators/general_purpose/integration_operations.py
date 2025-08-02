"""
Integration Operations Operator
Handles external API integrations, webhooks, and third-party service connections
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib
import hmac
from core.services.logger import get_logger

logger = get_logger(__name__)


class IntegrationOperationsOperator:
    """Integration operations manager for external service connections"""
    
    def __init__(self):
        """Initialize integration operations operator"""
        self.integrations = {}
        self.api_calls = {}
        self.webhooks = {}
        self.rate_limits = {}
        self.api_keys = {}
        logger.info("Integration operations operator initialized")
    
    def register_integration(self, integration_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new external integration"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        integration_id = core_ops.generate_operation_id("INTEGRATION")
        
        integration = {
            "integration_id": integration_id,
            "name": integration_config["name"],
            "provider": integration_config["provider"],
            "base_url": integration_config.get("base_url"),
            "api_version": integration_config.get("api_version", "v1"),
            "authentication_type": integration_config.get("auth_type", "api_key"),
            "rate_limit": integration_config.get("rate_limit", {"requests_per_minute": 60}),
            "timeout_seconds": integration_config.get("timeout_seconds", 30),
            "retry_attempts": integration_config.get("retry_attempts", 3),
            "retry_delay_seconds": integration_config.get("retry_delay_seconds", 1),
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "success_count": 0,
            "failure_count": 0
        }
        
        self.integrations[integration_id] = integration
        
        # Initialize rate limiting for this integration
        self.rate_limits[integration_id] = {
            "requests": [],
            "limit": integration["rate_limit"]["requests_per_minute"]
        }
        
        logger.info(f"Registered integration: {integration_config['name']} ({integration_id})")
        return integration
    
    def make_api_call(self, integration_id: str, endpoint: str, method: str = "GET",
                     data: Optional[Dict[str, Any]] = None, 
                     headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make API call to external service"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")
        
        integration = self.integrations[integration_id]
        
        # Check rate limiting
        if not self._check_rate_limit(integration_id):
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after_seconds": 60
            }
        
        call_id = core_ops.generate_operation_id("APICALL")
        start_time = datetime.now()
        
        api_call_record = {
            "call_id": call_id,
            "integration_id": integration_id,
            "endpoint": endpoint,
            "method": method,
            "request_data": data,
            "request_headers": headers,
            "timestamp": start_time.isoformat(),
            "status": "pending"
        }
        
        try:
            # Record rate limit usage
            self._record_rate_limit_usage(integration_id)
            
            # In a real implementation, this would make the actual HTTP request
            response = self._simulate_api_call(integration, endpoint, method, data, headers)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            api_call_record.update({
                "status": "completed",
                "response_data": response,
                "response_time_seconds": response_time,
                "completed_at": end_time.isoformat(),
                "success": response.get("success", True)
            })
            
            # Update integration statistics
            if response.get("success", True):
                integration["success_count"] += 1
            else:
                integration["failure_count"] += 1
            
            integration["last_used"] = start_time.isoformat()
            
            # Log the operation
            core_ops.log_operation("api_call", {
                "data": {
                    "call_id": call_id,
                    "integration_id": integration_id,
                    "endpoint": endpoint,
                    "method": method,
                    "success": response.get("success", True)
                }
            })
            
            logger.info(f"API call completed: {call_id} - {endpoint} ({response_time:.2f}s)")
            
        except Exception as e:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            api_call_record.update({
                "status": "failed",
                "error": str(e),
                "response_time_seconds": response_time,
                "completed_at": end_time.isoformat(),
                "success": False
            })
            
            integration["failure_count"] += 1
            logger.error(f"API call failed: {call_id} - {e}")
        
        self.api_calls[call_id] = api_call_record
        return api_call_record
    
    def _simulate_api_call(self, integration: Dict[str, Any], endpoint: str, 
                          method: str, data: Optional[Dict[str, Any]], 
                          headers: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Simulate API call response (for development/testing)"""
        # In a real implementation, this would use requests library or similar
        return {
            "success": True,
            "status_code": 200,
            "data": {"message": "Simulated response", "endpoint": endpoint},
            "headers": {"content-type": "application/json"}
        }
    
    def _check_rate_limit(self, integration_id: str) -> bool:
        """Check if API call is within rate limits"""
        if integration_id not in self.rate_limits:
            return True
        
        rate_data = self.rate_limits[integration_id]
        current_time = datetime.now()
        one_minute_ago = current_time - timedelta(minutes=1)
        
        # Remove old requests (older than 1 minute)
        rate_data["requests"] = [
            req_time for req_time in rate_data["requests"]
            if req_time > one_minute_ago
        ]
        
        # Check if we're under the limit
        return len(rate_data["requests"]) < rate_data["limit"]
    
    def _record_rate_limit_usage(self, integration_id: str) -> None:
        """Record API call for rate limiting"""
        if integration_id in self.rate_limits:
            self.rate_limits[integration_id]["requests"].append(datetime.now())
    
    def create_webhook(self, webhook_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create webhook endpoint"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        webhook_id = core_ops.generate_operation_id("WEBHOOK")
        
        webhook = {
            "webhook_id": webhook_id,
            "name": webhook_config["name"],
            "url_path": webhook_config.get("url_path", f"/webhooks/{webhook_id}"),
            "expected_events": webhook_config.get("events", []),
            "authentication_required": webhook_config.get("auth_required", True),
            "secret_key": webhook_config.get("secret_key"),
            "signature_header": webhook_config.get("signature_header", "X-Signature"),
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_received": None,
            "total_received": 0,
            "handler_function": webhook_config.get("handler")
        }
        
        self.webhooks[webhook_id] = webhook
        logger.info(f"Created webhook: {webhook_config['name']} ({webhook_id})")
        return webhook
    
    def process_webhook(self, webhook_id: str, payload: Dict[str, Any], 
                       headers: Dict[str, str]) -> Dict[str, Any]:
        """Process incoming webhook"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        if webhook_id not in self.webhooks:
            return {"success": False, "error": "Webhook not found"}
        
        webhook = self.webhooks[webhook_id]
        
        if not webhook["active"]:
            return {"success": False, "error": "Webhook inactive"}
        
        # Validate signature if required
        if webhook["authentication_required"]:
            if not self._validate_webhook_signature(webhook, payload, headers):
                return {"success": False, "error": "Invalid signature"}
        
        event_id = core_ops.generate_operation_id("WEBHOOK_EVENT")
        
        webhook_event = {
            "event_id": event_id,
            "webhook_id": webhook_id,
            "payload": payload,
            "headers": headers,
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        try:
            # Process webhook using handler function
            if webhook.get("handler_function"):
                result = webhook["handler_function"](payload, headers)
                webhook_event["result"] = result
                webhook_event["processed"] = True
            else:
                webhook_event["result"] = {"message": "No handler configured"}
                webhook_event["processed"] = True
            
            # Update webhook statistics
            webhook["total_received"] += 1
            webhook["last_received"] = datetime.now().isoformat()
            
            # Log the operation
            core_ops.log_operation("webhook_processed", {
                "data": {
                    "event_id": event_id,
                    "webhook_id": webhook_id,
                    "success": True
                }
            })
            
            logger.info(f"Processed webhook: {webhook_id} - {event_id}")
            return {"success": True, "event_id": event_id}
            
        except Exception as e:
            webhook_event["error"] = str(e)
            webhook_event["processed"] = False
            
            logger.error(f"Webhook processing failed: {webhook_id} - {e}")
            return {"success": False, "error": str(e), "event_id": event_id}
    
    def _validate_webhook_signature(self, webhook: Dict[str, Any], 
                                   payload: Dict[str, Any], 
                                   headers: Dict[str, str]) -> bool:
        """Validate webhook signature"""
        if not webhook.get("secret_key"):
            return True  # No secret configured, skip validation
        
        signature_header = webhook.get("signature_header", "X-Signature")
        received_signature = headers.get(signature_header)
        
        if not received_signature:
            return False
        
        # Calculate expected signature
        payload_string = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            webhook["secret_key"].encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(f"sha256={expected_signature}", received_signature)
    
    def get_integration_stats(self, integration_id: Optional[str] = None) -> Dict[str, Any]:
        """Get integration statistics"""
        if integration_id:
            if integration_id not in self.integrations:
                raise ValueError(f"Integration {integration_id} not found")
            
            integration = self.integrations[integration_id]
            
            # Get recent API calls for this integration
            recent_calls = [
                call for call in self.api_calls.values()
                if call["integration_id"] == integration_id
            ]
            
            total_calls = len(recent_calls)
            successful_calls = len([c for c in recent_calls if c.get("success", False)])
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            
            avg_response_time = 0
            if recent_calls:
                response_times = [c.get("response_time_seconds", 0) for c in recent_calls]
                avg_response_time = sum(response_times) / len(response_times)
            
            return {
                "integration_id": integration_id,
                "name": integration["name"],
                "provider": integration["provider"],
                "active": integration["active"],
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": total_calls - successful_calls,
                "success_rate_percent": round(success_rate, 2),
                "avg_response_time_seconds": round(avg_response_time, 3),
                "last_used": integration.get("last_used"),
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Return stats for all integrations
            all_stats = {}
            for int_id in self.integrations.keys():
                all_stats[int_id] = self.get_integration_stats(int_id)
            
            return {
                "total_integrations": len(self.integrations),
                "active_integrations": len([i for i in self.integrations.values() if i["active"]]),
                "integration_details": all_stats,
                "generated_at": datetime.now().isoformat()
            }
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook statistics"""
        total_webhooks = len(self.webhooks)
        active_webhooks = len([w for w in self.webhooks.values() if w["active"]])
        
        total_events = sum(w.get("total_received", 0) for w in self.webhooks.values())
        
        webhook_details = {}
        for webhook_id, webhook in self.webhooks.items():
            webhook_details[webhook_id] = {
                "name": webhook["name"],
                "active": webhook["active"],
                "total_received": webhook.get("total_received", 0),
                "last_received": webhook.get("last_received"),
                "url_path": webhook.get("url_path")
            }
        
        return {
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "total_events_received": total_events,
            "webhook_details": webhook_details,
            "generated_at": datetime.now().isoformat()
        }
