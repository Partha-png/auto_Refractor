"""
FastAPI webhook server for receiving GitHub events.
"""
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse
import hmac
import hashlib
from typing import Optional

from src.webhook.models import WebhookEvent
from src.webhook.handlers import (
    handle_pull_request_opened,
    handle_pull_request_synchronized,
    handle_pull_request_closed
)
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Auto-Refractor Webhook Server",
    description="GitHub webhook server for automated code refactoring",
    version="1.0.0"
)


def validate_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validate GitHub webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret from settings
        
    Returns:
        bool: True if signature is valid
    """
    if not secret:
        logger.warning("No webhook secret configured - signature validation disabled")
        return True  # Allow in development
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # GitHub sends signature as "sha256=<hash>"
    expected_signature = f"sha256={expected}"
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "auto-refractor-webhook",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "auto-refractor-webhook"
    }


@app.post("/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint.
    
    Receives PR events and triggers refactoring in background.
    
    Headers:
        X-Hub-Signature-256: HMAC signature for validation
        X-GitHub-Event: Event type (pull_request, push, etc.)
    """
    logger.info(f"Received webhook event: {x_github_event}")
    
    # Get raw body for signature validation
    body = await request.body()
    
    # Validate signature
    if x_hub_signature_256:
        if not validate_github_signature(
            body,
            x_hub_signature_256,
            settings.github_webhook_secret or ""
        ):
            logger.error("Invalid webhook signature")
            raise HTTPException(
                status_code=401,
                detail="Invalid signature"
            )
    else:
        logger.warning("No signature provided in webhook request")
    
    # Only handle pull_request events
    if x_github_event != "pull_request":
        logger.info(f"Ignoring event type: {x_github_event}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ignored",
                "reason": f"event type '{x_github_event}' not handled"
            }
        )
    
    try:
        data = await request.json()
        event = WebhookEvent(**data)
    except Exception as e:
        logger.error(f"Failed to parse webhook data: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid webhook data: {str(e)}"
        )
    
    # Route to appropriate handler (in background)
    action = event.action
    pr_number = event.pull_request.number
    
    if action == "opened":
        logger.info(f"Queuing handler for PR #{pr_number} (opened)")
        background_tasks.add_task(handle_pull_request_opened, event)
        
    elif action == "synchronize":
        logger.info(f"Queuing handler for PR #{pr_number} (synchronized)")
        background_tasks.add_task(handle_pull_request_synchronized, event)
        
    elif action == "closed":
        logger.info(f"Queuing handler for PR #{pr_number} (closed)")
        background_tasks.add_task(handle_pull_request_closed, event)
        
    else:
        logger.info(f"Ignoring PR action: {action}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ignored",
                "reason": f"action '{action}' not handled"
            }
        )
    
    # Return immediately (GitHub expects 200 within 10 seconds)
    logger.info(f"Webhook accepted: PR #{pr_number} ({action})")
    return JSONResponse(
        status_code=200,
        content={
            "status": "accepted",
            "pr_number": pr_number,
            "action": action,
            "message": "Processing in background"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    port = getattr(settings, 'webhook_port', 8000)
    host = getattr(settings, 'webhook_host', '0.0.0.0')
    
    logger.info(f"Starting webhook server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
