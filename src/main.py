# src/main.py
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from sqlmodel import Session, select, func
from models import User, Recognition, Endorsement, Redemption, AuditLog
from datetime import date, timedelta
from db import get_session, create_db_and_tables
from schemas import (
    CreateUserRequest, RecognizeRequest, RedeemRequest,
    UserResponse, RecognitionResponse, RedemptionResponse,
    EndorsementResponse, LeaderboardEntry, AuditLogResponse,
    LoginRequest, TokenResponse
)
from typing import List, Optional
from audit import log_action, get_client_ip
from auth import (
    get_current_user, get_current_admin_user,
    create_access_token, authenticate_user, hash_password
)

app = FastAPI(title="Boostly")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/register", response_model=UserResponse)
def register_user(req: CreateUserRequest, request: Request):
    """Register a new user with email and password."""
    with get_session() as s:
        # Check if email already exists
        existing = s.exec(select(User).where(User.email == req.email)).first()
        if existing:
            raise HTTPException(400, "Email already registered")
        
        # Hash password
        password_hash = hash_password(req.password)
        
        # Create user
        u = User(name=req.name, email=req.email, password_hash=password_hash)
        s.add(u)
        s.commit()
        s.refresh(u)
        
        # Audit log
        log_action(
            session=s,
            action="create_user",
            user_id=None,  # no authenticated user yet
            entity_type="user",
            entity_id=u.id,
            details={"name": u.name, "email": u.email},
            ip_address=get_client_ip(request)
        )
        s.commit()
        return u

@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request):
    """
    Authenticate user and return JWT access token.
    
    The JWT token includes:
    - sub: user_id
    - role: user role (admin or user)
    - exp: expiration timestamp
    """
    with get_session() as s:
        # Authenticate user
        user = authenticate_user(s, req.email, req.password)
        if not user:
            # Audit failed login attempt
            log_action(
                session=s,
                action="login_failed",
                user_id=None,
                entity_type="auth",
                entity_id=None,
                details={"email": req.email, "reason": "invalid_credentials"},
                ip_address=get_client_ip(request)
            )
            s.commit()
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Determine user role
        role = "admin" if user.id == 1 else "user"
        
        # Create access token with claims
        access_token = create_access_token(
            data={
                "sub": str(user.id),  # subject (user_id) must be string
                "role": role,
                "email": user.email,
                "name": user.name
            },
            expires_delta=timedelta(hours=24)
        )
        
        # Audit successful login
        log_action(
            session=s,
            action="login_success",
            user_id=user.id,
            entity_type="auth",
            entity_id=user.id,
            details={"email": user.email, "role": role},
            ip_address=get_client_ip(request)
        )
        s.commit()
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=role
        )

@app.post("/recognize", response_model=RecognitionResponse)
def recognize(req: RecognizeRequest, request: Request, sender: User = Depends(get_current_user)):
    if sender.id == req.receiver_id:
        raise HTTPException(400, "Cannot send credits to yourself")
    with get_session() as s:
        s.add(sender); s.refresh(sender)  # refresh to latest state
        if sender.grant_balance < req.credits:
            raise HTTPException(400, "Insufficient grant balance to send")
        if sender.sent_this_month + req.credits > 100:
            raise HTTPException(400, "Monthly sending limit exceeded")
        receiver = s.get(User, req.receiver_id)
        if not receiver:
            raise HTTPException(404, "Receiver not found")
        # create recognition and update balances atomically
        rec = Recognition(sender_id=sender.id, receiver_id=req.receiver_id, credits=req.credits, note=req.note)
        s.add(rec)
        sender.grant_balance -= req.credits
        sender.sent_this_month += req.credits
        receiver.redeemable_balance += req.credits
        receiver.total_received += req.credits
        s.add(sender); s.add(receiver)
        s.commit()
        s.refresh(rec)
        
        # Audit log
        log_action(
            session=s,
            action="recognize",
            user_id=sender.id,
            entity_type="recognition",
            entity_id=rec.id,
            details={
                "sender_id": sender.id,
                "receiver_id": req.receiver_id,
                "receiver_name": receiver.name,
                "credits": req.credits,
                "note": req.note,
                "sender_balance_after": sender.grant_balance,
                "receiver_balance_after": receiver.redeemable_balance
            },
            ip_address=get_client_ip(request)
        )
        s.commit()
        return RecognitionResponse(status="ok", recognition_id=rec.id)

@app.post("/recognitions/{rec_id}/endorse", response_model=EndorsementResponse)
def endorse(rec_id: int, request: Request, endorser: User = Depends(get_current_user)):
    if rec_id <= 0:
        raise HTTPException(400, "Invalid recognition ID")
    with get_session() as s:
        rec = s.get(Recognition, rec_id)
        if not rec:
            raise HTTPException(404, "Recognition not found")
        # check if endorser already endorsed
        q = select(Endorsement).where(Endorsement.recognition_id == rec_id, Endorsement.endorser_id == endorser.id)
        existing = s.exec(q).first()
        if existing:
            raise HTTPException(400, "Already endorsed")
        e = Endorsement(recognition_id=rec_id, endorser_id=endorser.id)
        s.add(e)
        s.commit()
        s.refresh(e)
        
        # Audit log
        log_action(
            session=s,
            action="endorse",
            user_id=endorser.id,
            entity_type="endorsement",
            entity_id=e.id,
            details={
                "recognition_id": rec_id,
                "endorser_id": endorser.id,
                "endorser_name": endorser.name
            },
            ip_address=get_client_ip(request)
        )
        s.commit()
        return EndorsementResponse(status="ok")

@app.post("/redeem", response_model=RedemptionResponse)
def redeem(req: RedeemRequest, request: Request, user: User = Depends(get_current_user)):
    with get_session() as s:
        s.add(user); s.refresh(user)
        if user.redeemable_balance < req.credits:
            raise HTTPException(400, "Insufficient redeemable balance")
        user.redeemable_balance -= req.credits
        voucher_value = req.credits * 5
        red = Redemption(user_id=user.id, credits=req.credits, value_in_inr=voucher_value)
        s.add(user); s.add(red)
        s.commit()
        s.refresh(red)
        
        # Audit log
        log_action(
            session=s,
            action="redeem",
            user_id=user.id,
            entity_type="redemption",
            entity_id=red.id,
            details={
                "credits": req.credits,
                "voucher_inr": voucher_value,
                "balance_after": user.redeemable_balance
            },
            ip_address=get_client_ip(request)
        )
        s.commit()
        return RedemptionResponse(status="ok", voucher_inr=voucher_value)

@app.post("/admin/reset_month")
def reset_month(request: Request, admin_user: User = Depends(get_current_admin_user)):
    today = date.today()
    with get_session() as s:
        users = s.exec(select(User)).all()
        reset_count = 0
        user_details = []
        
        for u in users:
            # only reset if not reset today (or month)
            if u.last_reset_date and u.last_reset_date.month == today.month and u.last_reset_date.year == today.year:
                continue
            unused = max(0, u.grant_balance)
            carry = min(50, unused)
            old_balance = u.grant_balance
            u.grant_balance = 100 + carry
            u.sent_this_month = 0
            u.last_reset_date = today
            s.add(u)
            reset_count += 1
            user_details.append({
                "user_id": u.id,
                "old_balance": old_balance,
                "new_balance": u.grant_balance,
                "carry_forward": carry
            })
        
        s.commit()
        
        # Audit log
        log_action(
            session=s,
            action="reset_month",
            user_id=admin_user.id,
            entity_type="system",
            entity_id=None,
            details={
                "reset_date": today.isoformat(),
                "users_reset": reset_count,
                "admin_id": admin_user.id,
                "admin_name": admin_user.name,
                "user_resets": user_details
            },
            ip_address=get_client_ip(request)
        )
        s.commit()
    return {"status":"ok", "users_reset": reset_count}

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard(limit: int = Query(default=10, gt=0, le=100)):
    with get_session() as s:
        users = s.exec(select(User).order_by(User.total_received.desc(), User.id.asc()).limit(limit)).all()
        result = []
        for u in users:
            rec_count = s.exec(select(func.count(Recognition.id)).where(Recognition.receiver_id == u.id)).first()
            end_count = s.exec(
                select(func.count(Endorsement.id)).join(Recognition, Endorsement.recognition_id == Recognition.id).where(Recognition.receiver_id == u.id)
            ).first()
            result.append(LeaderboardEntry(
                id=u.id, name=u.name, total_received=u.total_received,
                recognition_count=rec_count or 0, endorsement_total=end_count or 0
            ))
        return result

@app.get("/admin/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    admin_user: User = Depends(get_current_admin_user),
    limit: int = Query(default=100, gt=0, le=1000),
    action: Optional[str] = Query(default=None, description="Filter by action type"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID"),
    entity_type: Optional[str] = Query(default=None, description="Filter by entity type")
):
    """
    Get audit logs. Admin only endpoint.
    
    Query parameters:
    - limit: Number of logs to return (default: 100, max: 1000)
    - action: Filter by action type (e.g., "recognize", "redeem", "reset_month")
    - user_id: Filter by user who performed the action
    - entity_type: Filter by entity type (e.g., "recognition", "redemption")
    """
    
    with get_session() as s:
        # Build query with filters
        query = select(AuditLog).order_by(AuditLog.ts.desc())
        
        if action:
            query = query.where(AuditLog.action == action)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        
        query = query.limit(limit)
        
        logs = s.exec(query).all()
        
        # Convert to response format
        result = []
        for log in logs:
            result.append(AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                details=log.details,
                ip_address=log.ip_address,
                ts=log.ts.isoformat()
            ))
        
        return result
