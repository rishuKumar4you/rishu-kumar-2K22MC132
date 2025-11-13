# src/audit.py
from sqlmodel import Session
from models import AuditLog
from typing import Optional, Dict, Any
from fastapi import Request

def log_action(
    session: Session,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """
    Create an audit log entry for an action.
    
    Args:
        session: Database session
        action: Action name (e.g., "create_user", "recognize", "redeem")
        user_id: ID of user who performed the action
        entity_type: Type of entity affected (e.g., "user", "recognition")
        entity_id: ID of the affected entity
        details: Additional context as a dictionary
        ip_address: IP address of the requester
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            ip_address=ip_address
        )
        session.add(audit_entry)
        session.flush()  # flush to ensure it's written even if parent transaction fails later
    except Exception as e:
        # Don't let audit logging failure break the main operation
        # In production, you'd want to log this error to a monitoring system
        print(f"Audit logging failed: {e}")

def get_client_ip(request: Request) -> Optional[str]:
    """
    Extract client IP address from request, handling proxies.
    """
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client
    if request.client:
        return request.client.host
    
    return None

