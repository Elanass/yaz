"""SMART on FHIR Router - Healthcare App Integration

Provides SMART on FHIR OAuth endpoints for EHR integration,
launch context handling, and SMART app authorization flows.
"""

import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel

from infra.clients.smart_client import SMARTClient, SMARTError, create_smart_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/smart", tags=["SMART on FHIR"])


# Dependency to get SMART client
async def get_smart_client() -> SMARTClient:
    """Get configured SMART client"""
    return create_smart_client()


# Request/Response Models
class AuthorizeRequest(BaseModel):
    """SMART authorization request"""
    response_type: str = "code"
    client_id: str
    redirect_uri: str
    scope: str
    state: str
    aud: str
    launch: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None


class TokenRequest(BaseModel):
    """Token exchange request"""
    grant_type: str
    code: str
    redirect_uri: str
    client_id: str
    client_secret: Optional[str] = None
    code_verifier: Optional[str] = None


class LaunchRequest(BaseModel):
    """EHR launch request"""
    iss: str  # FHIR server URL
    launch: str  # Launch context token


# In-memory session storage (replace with Redis/database in production)
session_store: Dict[str, Dict[str, Any]] = {}


# Error handler for SMART errors
async def smart_error_handler(request: Request, exc: SMARTError):
    """Handle SMART-specific errors"""
    logger.error(f"SMART Error: {exc}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.error_code or "invalid_request",
            "error_description": str(exc),
            "details": exc.response if exc.response else None
        }
    )


# Well-Known Configuration
@router.get("/.well-known/smart-configuration")
async def get_smart_configuration(
    request: Request,
    client: SMARTClient = Depends(get_smart_client)
):
    """SMART on FHIR well-known configuration endpoint"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    config = client.get_well_known_config(base_url)
    return config


# EHR Launch Endpoint
@router.get("/launch")
async def ehr_launch(
    iss: str,
    launch: str,
    request: Request,
    client: SMARTClient = Depends(get_smart_client)
):
    """
    EHR launch endpoint - initiated from within EHR
    
    This endpoint receives the initial launch request from an EHR
    and redirects to the authorization server.
    """
    logger.info(f"EHR Launch: iss={iss}, launch={launch}")
    
    async with client:
        try:
            # Build authorization URL with launch context
            auth_url, session_data = await client.build_authorization_url(
                fhir_base_url=iss,
                scopes=["launch", "patient/*.read", "user/*.read", "openid", "profile"],
                launch=launch
            )
            
            # Store session data (use proper session management in production)
            session_id = session_data["state"]
            session_store[session_id] = session_data
            
            logger.info(f"Redirecting to authorization: {auth_url}")
            return RedirectResponse(url=auth_url)
            
        except SMARTError as e:
            logger.error(f"EHR launch failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


# Standalone Launch
@router.get("/standalone")
async def standalone_launch(
    request: Request,
    iss: Optional[str] = None,
    client: SMARTClient = Depends(get_smart_client)
):
    """
    Standalone launch - app chooses FHIR server
    
    This endpoint allows the app to launch independently
    and connect to a chosen FHIR server.
    """
    # Default FHIR server if not provided
    fhir_server = iss or "https://r4.smarthealthit.org"
    
    logger.info(f"Standalone Launch: iss={fhir_server}")
    
    async with client:
        try:
            # Build authorization URL without launch context
            auth_url, session_data = await client.build_authorization_url(
                fhir_base_url=fhir_server,
                scopes=["patient/*.read", "user/*.read", "openid", "profile"]
            )
            
            # Store session data
            session_id = session_data["state"]
            session_store[session_id] = session_data
            
            logger.info(f"Redirecting to authorization: {auth_url}")
            return RedirectResponse(url=auth_url)
            
        except SMARTError as e:
            logger.error(f"Standalone launch failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


# Authorization Endpoint (for apps that we authorize)
@router.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    aud: str,
    launch: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    request: Request = None
):
    """
    Authorization endpoint for SMART apps
    
    This endpoint would be used if we're acting as an authorization server
    for other SMART apps.
    """
    # Basic validation
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only authorization code flow supported")
    
    # In a real implementation, you would:
    # 1. Validate client_id
    # 2. Show user consent screen
    # 3. Generate authorization code
    # 4. Redirect back with code
    
    # For demo purposes, return a simple consent page
    consent_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMART App Authorization</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .consent-box {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; }}
            .app-info {{ background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0; }}
            .scopes {{ background: #fff3cd; padding: 15px; border-radius: 4px; margin: 10px 0; }}
            .buttons {{ margin-top: 20px; }}
            button {{ padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }}
            .allow {{ background: #28a745; color: white; }}
            .deny {{ background: #dc3545; color: white; }}
        </style>
    </head>
    <body>
        <div class="consent-box">
            <h2>App Authorization Request</h2>
            
            <div class="app-info">
                <strong>App:</strong> {client_id}<br>
                <strong>FHIR Server:</strong> {aud}<br>
                <strong>Redirect URI:</strong> {redirect_uri}
            </div>
            
            <div class="scopes">
                <strong>Requested Permissions:</strong><br>
                {scope.replace(' ', '<br>')}
            </div>
            
            <p>This app is requesting access to your health data. Do you want to allow this?</p>
            
            <div class="buttons">
                <form method="post" action="/smart/authorize/consent" style="display: inline;">
                    <input type="hidden" name="client_id" value="{client_id}">
                    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                    <input type="hidden" name="state" value="{state}">
                    <input type="hidden" name="scope" value="{scope}">
                    <input type="hidden" name="aud" value="{aud}">
                    <button type="submit" name="consent" value="allow" class="allow">Allow</button>
                    <button type="submit" name="consent" value="deny" class="deny">Deny</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=consent_html)


@router.post("/authorize/consent")
async def handle_consent(
    consent: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
    scope: str = Form(...),
    aud: str = Form(...)
):
    """Handle user consent for authorization"""
    if consent == "deny":
        # Redirect with error
        error_url = f"{redirect_uri}?error=access_denied&state={state}"
        return RedirectResponse(url=error_url)
    
    # Generate authorization code (in production, store in database)
    import secrets
    auth_code = secrets.token_urlsafe(32)
    
    # Store authorization code with associated data
    session_store[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "aud": aud,
        "expires_at": "2025-08-11T01:00:00Z"  # 1 hour expiration
    }
    
    # Redirect with authorization code
    callback_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=callback_url)


# OAuth Callback Endpoint
@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    client: SMARTClient = Depends(get_smart_client)
):
    """
    OAuth callback endpoint - receives authorization code
    
    This endpoint receives the authorization code after user consent
    and exchanges it for an access token.
    """
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        raise HTTPException(status_code=400, detail=f"Authorization failed: {error}")
    
    # Retrieve session data
    session_data = session_store.get(state)
    if not session_data:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    async with client:
        try:
            # Exchange code for token
            token_response = await client.exchange_code_for_token(code, session_data)
            
            # Parse launch context
            launch_context = client.parse_launch_context(token_response)
            
            # Clean up session
            del session_store[state]
            
            # In a real app, you would store the token securely and redirect to the app
            # For demo, return token info (DO NOT do this in production)
            return {
                "message": "Authorization successful",
                "access_token": token_response.access_token[:10] + "...",  # Partial token for demo
                "token_type": token_response.token_type,
                "expires_in": token_response.expires_in,
                "scope": token_response.scope,
                "patient": token_response.patient,
                "launch_context": launch_context.dict()
            }
            
        except SMARTError as e:
            logger.error(f"Token exchange failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


# Token Endpoint
@router.post("/token")
async def token_endpoint(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None)
):
    """
    Token endpoint for SMART apps
    
    Exchanges authorization code for access token.
    """
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Only authorization code grant supported")
    
    # Validate authorization code
    auth_data = session_store.get(code)
    if not auth_data:
        raise HTTPException(status_code=400, detail="Invalid authorization code")
    
    # Validate client
    if auth_data["client_id"] != client_id:
        raise HTTPException(status_code=400, detail="Client mismatch")
    
    if auth_data["redirect_uri"] != redirect_uri:
        raise HTTPException(status_code=400, detail="Redirect URI mismatch")
    
    # Generate access token (in production, use proper JWT)
    import secrets
    access_token = secrets.token_urlsafe(64)
    
    # Clean up authorization code
    del session_store[code]
    
    # Return token response
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": auth_data["scope"],
        "patient": "example-patient-id",  # Would come from launch context
        "need_patient_banner": True,
        "smart_style_url": "https://example.com/smart-style.json"
    }


# Token Introspection
@router.post("/introspect")
async def introspect_token(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None)
):
    """
    Token introspection endpoint
    
    Provides information about an access token.
    """
    # In a real implementation, validate and look up token
    # For demo, return basic info
    return {
        "active": True,
        "scope": "patient/*.read user/*.read",
        "client_id": "demo-client",
        "exp": 1691712000,  # Expiration timestamp
        "aud": "https://r4.smarthealthit.org",
        "patient": "example-patient-id"
    }


# Refresh Token
@router.post("/refresh")
async def refresh_token(
    grant_type: str = Form(...),
    refresh_token: str = Form(...),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    client: SMARTClient = Depends(get_smart_client)
):
    """Refresh access token using refresh token"""
    if grant_type != "refresh_token":
        raise HTTPException(status_code=400, detail="Invalid grant type")
    
    # In a real implementation, validate refresh token and generate new access token
    import secrets
    new_access_token = secrets.token_urlsafe(64)
    new_refresh_token = secrets.token_urlsafe(64)
    
    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": new_refresh_token,
        "scope": "patient/*.read user/*.read"
    }


# Health Check
@router.get("/health")
async def health_check():
    """Check SMART service health"""
    return {
        "status": "healthy",
        "service": "SMART on FHIR",
        "endpoints": {
            "launch": "/smart/launch",
            "authorize": "/smart/authorize", 
            "token": "/smart/token",
            "configuration": "/smart/.well-known/smart-configuration"
        },
        "timestamp": "2025-08-11T00:00:00Z"
    }


# Demo Page
@router.get("/demo")
async def smart_demo(request: Request):
    """Demo page for SMART app launch"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    demo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMART on FHIR Demo</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .demo-section {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .launch-button {{ padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }}
            .launch-button:hover {{ background: #0056b3; }}
            code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>SMART on FHIR Demo</h1>
        
        <div class="demo-section">
            <h2>Standalone Launch</h2>
            <p>Launch the app independently and choose a FHIR server:</p>
            <a href="/smart/standalone" class="launch-button">Launch Standalone</a>
            <a href="/smart/standalone?iss=https://r4.smarthealthit.org" class="launch-button">Launch with SMART Sandbox</a>
        </div>
        
        <div class="demo-section">
            <h2>EHR Launch</h2>
            <p>Simulate launch from within an EHR:</p>
            <a href="/smart/launch?iss=https://r4.smarthealthit.org&launch=demo-launch-123" class="launch-button">Simulate EHR Launch</a>
        </div>
        
        <div class="demo-section">
            <h2>Configuration</h2>
            <p>SMART configuration endpoint:</p>
            <a href="/smart/.well-known/smart-configuration" target="_blank"><code>/smart/.well-known/smart-configuration</code></a>
        </div>
        
        <div class="demo-section">
            <h2>Integration</h2>
            <p>To integrate with an EHR, register this app with:</p>
            <ul>
                <li><strong>Client ID:</strong> yaz-healthcare-platform</li>
                <li><strong>Redirect URI:</strong> {base_url}/smart/callback</li>
                <li><strong>Launch URI:</strong> {base_url}/smart/launch</li>
                <li><strong>Scopes:</strong> launch patient/*.read user/*.read openid profile</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=demo_html)
