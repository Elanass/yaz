"""
Healthcare Compliance Middleware
HIPAA/GDPR compliant middleware for gastric oncology platform
"""

import time
import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.config.platform_config import config
from core.services.logger import get_logger
from core.services.encryption import encrypt_sensitive_data, decrypt_sensitive_data

logger = get_logger(__name__)


class HIPAAComplianceMiddleware(BaseHTTPMiddleware):
    """
    HIPAA compliance middleware for healthcare data protection
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.sensitive_endpoints = {
            "/api/v1/patients",
            "/api/v1/clinical",
            "/api/v1/decisions",
            "/api/v1/outcomes"
        }
        self.audit_log_file = config.audit_log_file
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with HIPAA compliance checks"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        try:
            # Pre-process security checks
            await self._validate_request_security(request)
            
            # Log access attempt
            await self._log_access_attempt(request, request_id)
            
            # Process request
            response = await call_next(request)
            
            # Post-process compliance
            await self._ensure_response_compliance(request, response, request_id)
            
            # Log successful access
            await self._log_successful_access(request, response, request_id, start_time)
            
            return response
            
        except HTTPException as e:
            # Log failed access
            await self._log_failed_access(request, e, request_id, start_time)
            raise
        except Exception as e:
            # Log system error
            await self._log_system_error(request, e, request_id, start_time)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id}
            )
    
    async def _validate_request_security(self, request: Request):
        """Validate request meets security requirements"""
        path = request.url.path
        
        # Check if accessing sensitive endpoint
        if any(path.startswith(endpoint) for endpoint in self.sensitive_endpoints):
            # Require authentication for sensitive endpoints
            auth_header = request.headers.get("authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required for accessing patient data"
                )
            
            # Validate secure connection in production
            if config.environment == "production":
                if not request.url.scheme == "https":
                    raise HTTPException(
                        status_code=403,
                        detail="HTTPS required for accessing patient data"
                    )
        
        # Rate limiting for sensitive endpoints
        await self._check_rate_limiting(request)
    
    async def _check_rate_limiting(self, request: Request):
        """Implement rate limiting for API protection"""
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # In a real implementation, this would use Redis or similar
        # For now, we'll log the attempt
        logger.info(f"Rate limit check for {client_ip} accessing {path}")
    
    async def _log_access_attempt(self, request: Request, request_id: str):
        """Log access attempt for audit trail"""
        audit_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "event": "access_attempt",
            "method": request.method,
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "user_id": getattr(request.state, "user_id", None),
            "session_id": self._get_session_id(request)
        }
        
        await self._write_audit_log(audit_data)
    
    async def _log_successful_access(self, request: Request, response: Response, 
                                   request_id: str, start_time: float):
        """Log successful access"""
        processing_time = time.time() - start_time
        
        audit_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "event": "access_success",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "client_ip": self._get_client_ip(request),
            "user_id": getattr(request.state, "user_id", None),
            "data_accessed": self._is_patient_data_accessed(request.url.path)
        }
        
        await self._write_audit_log(audit_data)
    
    async def _log_failed_access(self, request: Request, error: HTTPException, 
                                request_id: str, start_time: float):
        """Log failed access attempt"""
        processing_time = time.time() - start_time
        
        audit_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "event": "access_failed",
            "method": request.method,
            "path": request.url.path,
            "status_code": error.status_code,
            "error_detail": error.detail,
            "processing_time_ms": round(processing_time * 1000, 2),
            "client_ip": self._get_client_ip(request),
            "user_id": getattr(request.state, "user_id", None)
        }
        
        await self._write_audit_log(audit_data)
    
    async def _log_system_error(self, request: Request, error: Exception, 
                               request_id: str, start_time: float):
        """Log system error"""
        processing_time = time.time() - start_time
        
        audit_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "event": "system_error",
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "processing_time_ms": round(processing_time * 1000, 2),
            "client_ip": self._get_client_ip(request)
        }
        
        await self._write_audit_log(audit_data)
    
    async def _ensure_response_compliance(self, request: Request, response: Response, 
                                        request_id: str):
        """Ensure response meets compliance requirements"""
        # Add security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        if config.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server information
        response.headers.pop("server", None)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request"""
        # Try to get from cookie or header
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = request.headers.get("x-session-id")
        
        return session_id
    
    def _is_patient_data_accessed(self, path: str) -> bool:
        """Check if the request accessed patient data"""
        patient_data_indicators = [
            "/patients/", "/clinical/", "/decisions/", "/outcomes/"
        ]
        return any(indicator in path for indicator in patient_data_indicators)
    
    async def _write_audit_log(self, audit_data: Dict[str, Any]):
        """Write audit log entry"""
        try:
            # In a real implementation, this would write to a secure audit log
            # For now, we'll use structured logging
            logger.info(f"HIPAA_AUDIT: {json.dumps(audit_data)}")
            
            # TODO: Implement secure audit log storage
            # This could write to a separate database, file, or external service
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


class DataAnonymizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic data anonymization in responses
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.anonymization_enabled = config.enable_data_anonymization
        self.sensitive_fields = {
            "medical_record_number",
            "external_id", 
            "social_security_number",
            "phone_number",
            "email",
            "address"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process response with data anonymization"""
        if not self.anonymization_enabled:
            return await call_next(request)
        
        response = await call_next(request)
        
        # Check if user has permission for full data access
        user_role = getattr(request.state, "user_role", None)
        if user_role in ["admin", "primary_clinician"]:
            return response
        
        # Anonymize response data if needed
        if self._should_anonymize_response(request, response):
            return await self._anonymize_response_data(response)
        
        return response
    
    def _should_anonymize_response(self, request: Request, response: Response) -> bool:
        """Determine if response should be anonymized"""
        # Check content type
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return False
        
        # Check if accessing patient data
        path = request.url.path
        return any(path.startswith(endpoint) for endpoint in [
            "/api/v1/patients", "/api/v1/clinical"
        ])
    
    async def _anonymize_response_data(self, response: Response) -> Response:
        """Anonymize sensitive data in response"""
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parse JSON
            data = json.loads(body.decode())
            
            # Anonymize data
            anonymized_data = self._anonymize_data_recursive(data)
            
            # Create new response
            new_body = json.dumps(anonymized_data).encode()
            
            return Response(
                content=new_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )
            
        except Exception as e:
            logger.error(f"Failed to anonymize response data: {e}")
            return response
    
    def _anonymize_data_recursive(self, data: Any) -> Any:
        """Recursively anonymize data structure"""
        if isinstance(data, dict):
            anonymized = {}
            for key, value in data.items():
                if key in self.sensitive_fields:
                    anonymized[key] = self._anonymize_field_value(key, value)
                else:
                    anonymized[key] = self._anonymize_data_recursive(value)
            return anonymized
        
        elif isinstance(data, list):
            return [self._anonymize_data_recursive(item) for item in data]
        
        else:
            return data
    
    def _anonymize_field_value(self, field_name: str, value: Any) -> str:
        """Anonymize a specific field value"""
        if value is None:
            return None
        
        value_str = str(value)
        
        # Create consistent hash for the same value
        hash_input = f"{field_name}:{value_str}:{config.encryption_key}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        
        # Return anonymized value with field type prefix
        if field_name == "medical_record_number":
            return f"MRN-{hash_value}"
        elif field_name == "external_id":
            return f"EXT-{hash_value}"
        elif field_name in ["phone_number"]:
            return f"XXX-XXX-{hash_value[:4]}"
        elif field_name == "email":
            return f"user-{hash_value}@anonymized.com"
        else:
            return f"[ANONYMIZED-{hash_value}]"


class ElectricSQLSyncMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle ElectricSQL synchronization
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.sync_enabled = config.enable_offline_sync
        self.collaboration_enabled = config.enable_real_time_collaboration
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle ElectricSQL sync operations"""
        # Add sync headers to response
        response = await call_next(request)
        
        if self.sync_enabled:
            response.headers["X-Electric-Sync"] = "enabled"
            response.headers["X-Electric-Version"] = str(int(time.time()))
        
        if self.collaboration_enabled:
            response.headers["X-Electric-Collaboration"] = "enabled"
        
        # Handle sync requests
        if request.headers.get("x-electric-sync-request"):
            await self._handle_sync_request(request, response)
        
        return response
    
    async def _handle_sync_request(self, request: Request, response: Response):
        """Handle ElectricSQL sync request"""
        try:
            sync_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, "request_id", "unknown"),
                "user_id": getattr(request.state, "user_id", None),
                "sync_version": request.headers.get("x-electric-sync-version"),
                "tables": request.headers.get("x-electric-sync-tables", "").split(",")
            }
            
            logger.info(f"ElectricSQL sync request: {json.dumps(sync_data)}")
            
            # Add sync metadata to response
            response.headers["X-Electric-Sync-Processed"] = "true"
            response.headers["X-Electric-Sync-Timestamp"] = sync_data["timestamp"]
            
        except Exception as e:
            logger.error(f"Failed to handle sync request: {e}")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API performance and healthcare-specific metrics
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.slow_query_threshold = 2.0  # 2 seconds
        self.critical_endpoints = {
            "/api/v1/decisions": 1.0,  # 1 second for decision endpoints
            "/api/v1/emergency": 0.5   # 500ms for emergency endpoints
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance"""
        start_time = time.time()
        
        response = await call_next(request)
        
        processing_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
        
        # Check for slow responses
        await self._check_performance_thresholds(request, processing_time)
        
        # Log performance metrics
        await self._log_performance_metrics(request, response, processing_time)
        
        return response
    
    async def _check_performance_thresholds(self, request: Request, processing_time: float):
        """Check if response time exceeds thresholds"""
        path = request.url.path
        
        # Check critical endpoint thresholds
        for endpoint, threshold in self.critical_endpoints.items():
            if path.startswith(endpoint) and processing_time > threshold:
                logger.warning(
                    f"Critical endpoint {path} exceeded threshold: "
                    f"{processing_time:.3f}s > {threshold}s"
                )
                return
        
        # Check general slow query threshold
        if processing_time > self.slow_query_threshold:
            logger.warning(
                f"Slow response detected for {path}: {processing_time:.3f}s"
            )
    
    async def _log_performance_metrics(self, request: Request, response: Response, 
                                     processing_time: float):
        """Log performance metrics"""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "user_agent": request.headers.get("user-agent", "unknown")[:100],
            "content_length": response.headers.get("content-length", 0)
        }
        
        logger.info(f"PERFORMANCE_METRICS: {json.dumps(metrics)}")


# Middleware registration function
def register_healthcare_middleware(app):
    """Register all healthcare compliance middleware"""
    
    # Performance monitoring (first - to measure total time)
    app.add_middleware(PerformanceMonitoringMiddleware)
    
    # HIPAA compliance (core security)
    app.add_middleware(HIPAAComplianceMiddleware)
    
    # Data anonymization (data protection)
    app.add_middleware(DataAnonymizationMiddleware)
    
    # ElectricSQL sync (last - to handle sync operations)
    app.add_middleware(ElectricSQLSyncMiddleware)
    
    logger.info("Healthcare compliance middleware registered")
