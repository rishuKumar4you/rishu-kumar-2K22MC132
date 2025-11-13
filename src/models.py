from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    # monthly credits to SEND (resets to 100 monthly, carry-forward up to 50)
    grant_balance: int = 100
    # sum of credits the user has sent this month (for limiting to 100)
    sent_this_month: int = 0
    # credits the user has RECEIVED which they can redeem
    redeemable_balance: int = 0
    # totals for leaderboard
    total_received: int = 0
    last_reset_date: Optional[date] = None

class Recognition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int
    receiver_id: int
    credits: int
    note: Optional[str] = None
    ts: datetime = Field(default_factory=datetime.utcnow)

class Endorsement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recognition_id: int
    endorser_id: int
    ts: datetime = Field(default_factory=datetime.utcnow)

class Redemption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    credits: int
    value_in_inr: int
    ts: datetime = Field(default_factory=datetime.utcnow)
