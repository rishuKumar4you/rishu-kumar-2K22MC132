# src/main.py
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlmodel import Session, select, func
from models import User, Recognition, Endorsement, Redemption
from datetime import date
from db import get_session, create_db_and_tables

app = FastAPI(title="Boostly")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Simple API-key auth for demo: header x-api-user -> user id (int)
async def get_requesting_user(x_api_user: int = Header(...)):
    # In demo, client sets header x-api-user: <user_id>
    with get_session() as s:
        user = s.get(User, x_api_user)
        if not user:
            raise HTTPException(401, "Invalid user token")
        return user

@app.post("/users", response_model=User)
def create_user(name: str, email: str):
    with get_session() as s:
        u = User(name=name, email=email)
        s.add(u); s.commit(); s.refresh(u)
        return u

@app.post("/recognize")
def recognize(receiver_id: int, credits: int, note: str = None, sender: User = Depends(get_requesting_user)):
    if sender.id == receiver_id:
        raise HTTPException(400, "Cannot send credits to yourself")
    if credits <= 0:
        raise HTTPException(400, "Credits must be positive")
    with get_session() as s:
        s.add(sender); s.refresh(sender)  # refresh to latest state
        if sender.grant_balance < credits:
            raise HTTPException(400, "Insufficient grant balance to send")
        if sender.sent_this_month + credits > 100:
            raise HTTPException(400, "Monthly sending limit exceeded")
        receiver = s.get(User, receiver_id)
        if not receiver:
            raise HTTPException(404, "Receiver not found")
        # create recognition and update balances atomically
        rec = Recognition(sender_id=sender.id, receiver_id=receiver_id, credits=credits, note=note)
        s.add(rec)
        sender.grant_balance -= credits
        sender.sent_this_month += credits
        receiver.redeemable_balance += credits
        receiver.total_received += credits
        s.add(sender); s.add(receiver)
        s.commit()
        s.refresh(rec)
        return {"status":"ok", "recognition_id": rec.id}

@app.post("/recognitions/{rec_id}/endorse")
def endorse(rec_id: int, endorser: User = Depends(get_requesting_user)):
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
        s.add(e); s.commit()
        return {"status":"ok"}

@app.post("/redeem")
def redeem(credits: int, user: User = Depends(get_requesting_user)):
    if credits <= 0:
        raise HTTPException(400, "invalid credits")
    with get_session() as s:
        s.add(user); s.refresh(user)
        if user.redeemable_balance < credits:
            raise HTTPException(400, "Insufficient redeemable balance")
        user.redeemable_balance -= credits
        voucher_value = credits * 5
        red = Redemption(user_id=user.id, credits=credits, value_in_inr=voucher_value)
        s.add(user); s.add(red)
        s.commit()
        return {"status":"ok", "voucher_inr": voucher_value}

@app.post("/admin/reset_month")
def reset_month(admin_user: User = Depends(get_requesting_user)):
    # For demo allow only user id 1 as admin or check admin flag
    if admin_user.id != 1:
        raise HTTPException(403, "forbidden")
    today = date.today()
    with get_session() as s:
        users = s.exec(select(User)).all()
        for u in users:
            # only reset if not reset today (or month)
            if u.last_reset_date and u.last_reset_date.month == today.month and u.last_reset_date.year == today.year:
                continue
            unused = max(0, u.grant_balance)
            carry = min(50, unused)
            u.grant_balance = 100 + carry
            u.sent_this_month = 0
            u.last_reset_date = today
            s.add(u)
        s.commit()
    return {"status":"ok"}

@app.get("/leaderboard")
def leaderboard(limit: int = 10):
    with get_session() as s:
        users = s.exec(select(User).order_by(User.total_received.desc(), User.id.asc()).limit(limit)).all()
        result = []
        for u in users:
            rec_count = s.exec(select(func.count(Recognition.id)).where(Recognition.receiver_id == u.id)).first()
            end_count = s.exec(
                select(func.count(Endorsement.id)).join(Recognition, Endorsement.recognition_id == Recognition.id).where(Recognition.receiver_id == u.id)
            ).first()
            result.append({
                "id": u.id, "name": u.name, "total_received": u.total_received,
                "recognition_count": rec_count or 0, "endorsement_total": end_count or 0
            })
        return result
