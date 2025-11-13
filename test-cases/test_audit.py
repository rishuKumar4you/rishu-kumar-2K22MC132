#!/usr/bin/env python3
"""
Test script to demonstrate audit logging functionality
This script shows how audit logs capture all critical actions
"""

import sys
sys.path.insert(0, 'src')

from models import AuditLog, User
from db import get_session, create_db_and_tables
from audit import log_action

def test_audit_logging():
    print("\n=== Testing Audit Logging System ===\n")
    
    # Create database tables
    create_db_and_tables()
    print("✓ Database tables created")
    
    with get_session() as session:
        # Test 1: Log a user creation
        print("\n1. Testing user creation audit log...")
        log_action(
            session=session,
            action="create_user",
            user_id=None,
            entity_type="user",
            entity_id=1,
            details={"name": "Test User", "email": "test@example.com"},
            ip_address="127.0.0.1"
        )
        session.commit()
        print("   ✓ User creation logged")
        
        # Test 2: Log a recognition
        print("\n2. Testing recognition audit log...")
        log_action(
            session=session,
            action="recognize",
            user_id=1,
            entity_type="recognition",
            entity_id=1,
            details={
                "sender_id": 1,
                "receiver_id": 2,
                "credits": 10,
                "note": "Great work!",
                "sender_balance_after": 90,
                "receiver_balance_after": 10
            },
            ip_address="127.0.0.1"
        )
        session.commit()
        print("   ✓ Recognition logged")
        
        # Test 3: Log a redemption
        print("\n3. Testing redemption audit log...")
        log_action(
            session=session,
            action="redeem",
            user_id=2,
            entity_type="redemption",
            entity_id=1,
            details={
                "credits": 10,
                "voucher_inr": 50,
                "balance_after": 0
            },
            ip_address="127.0.0.1"
        )
        session.commit()
        print("   ✓ Redemption logged")
        
        # Test 4: Log a month reset
        print("\n4. Testing month reset audit log...")
        log_action(
            session=session,
            action="reset_month",
            user_id=1,
            entity_type="system",
            entity_id=None,
            details={
                "reset_date": "2025-01-01",
                "users_reset": 10,
                "admin_id": 1,
                "admin_name": "Admin User"
            },
            ip_address="127.0.0.1"
        )
        session.commit()
        print("   ✓ Month reset logged")
        
        # Test 5: Log an endorsement
        print("\n5. Testing endorsement audit log...")
        log_action(
            session=session,
            action="endorse",
            user_id=3,
            entity_type="endorsement",
            entity_id=1,
            details={
                "recognition_id": 1,
                "endorser_id": 3,
                "endorser_name": "Endorser User"
            },
            ip_address="127.0.0.1"
        )
        session.commit()
        print("   ✓ Endorsement logged")
        
        # Query and display all audit logs
        print("\n=== Retrieving Audit Logs ===\n")
        from sqlmodel import select
        logs = session.exec(select(AuditLog).order_by(AuditLog.ts.desc())).all()
        
        print(f"Total audit logs: {len(logs)}\n")
        
        for i, log in enumerate(logs, 1):
            print(f"{i}. Action: {log.action}")
            print(f"   User ID: {log.user_id}")
            print(f"   Entity: {log.entity_type} (ID: {log.entity_id})")
            print(f"   IP Address: {log.ip_address}")
            print(f"   Timestamp: {log.ts}")
            print(f"   Details: {log.details}")
            print()
        
        # Test filtering by action
        print("=== Testing Filters ===\n")
        
        recognize_logs = session.exec(
            select(AuditLog).where(AuditLog.action == "recognize")
        ).all()
        print(f"✓ Recognize actions: {len(recognize_logs)}")
        
        redeem_logs = session.exec(
            select(AuditLog).where(AuditLog.action == "redeem")
        ).all()
        print(f"✓ Redeem actions: {len(redeem_logs)}")
        
        user1_logs = session.exec(
            select(AuditLog).where(AuditLog.user_id == 1)
        ).all()
        print(f"✓ Actions by user 1: {len(user1_logs)}")
        
    print("\n✓ All audit logging tests completed successfully!\n")

if __name__ == "__main__":
    test_audit_logging()
