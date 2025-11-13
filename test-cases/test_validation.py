#!/usr/bin/env python3
"""Test script to verify Pydantic validation is working"""

from schemas import CreateUserRequest, RecognizeRequest, RedeemRequest
from pydantic import ValidationError

def test_create_user_validation():
    print("\n=== Testing CreateUserRequest Validation ===")
    
    # Valid user
    try:
        valid_user = CreateUserRequest(name="John Doe", email="john@example.com")
        print(f"✓ Valid user: {valid_user.name}, {valid_user.email}")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Invalid email
    try:
        CreateUserRequest(name="John Doe", email="invalid-email")
        print("✗ Should have failed with invalid email")
    except ValidationError as e:
        print(f"✓ Correctly rejected invalid email: {e.errors()[0]['msg']}")
    
    # Empty name
    try:
        CreateUserRequest(name="   ", email="john@example.com")
        print("✗ Should have failed with empty name")
    except ValidationError as e:
        print(f"✓ Correctly rejected empty name: {e.errors()[0]['msg']}")
    
    # Name too long
    try:
        CreateUserRequest(name="A" * 101, email="john@example.com")
        print("✗ Should have failed with name too long")
    except ValidationError as e:
        print(f"✓ Correctly rejected name too long: {e.errors()[0]['msg']}")

def test_recognize_validation():
    print("\n=== Testing RecognizeRequest Validation ===")
    
    # Valid recognition
    try:
        valid = RecognizeRequest(receiver_id=2, credits=10, note="Great work!")
        print(f"✓ Valid recognition: {valid.credits} credits to user {valid.receiver_id}")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Invalid receiver_id (0 or negative)
    try:
        RecognizeRequest(receiver_id=0, credits=10)
        print("✗ Should have failed with receiver_id = 0")
    except ValidationError as e:
        print(f"✓ Correctly rejected receiver_id = 0: {e.errors()[0]['msg']}")
    
    # Invalid credits (0)
    try:
        RecognizeRequest(receiver_id=2, credits=0)
        print("✗ Should have failed with credits = 0")
    except ValidationError as e:
        print(f"✓ Correctly rejected credits = 0: {e.errors()[0]['msg']}")
    
    # Invalid credits (> 100)
    try:
        RecognizeRequest(receiver_id=2, credits=101)
        print("✗ Should have failed with credits > 100")
    except ValidationError as e:
        print(f"✓ Correctly rejected credits > 100: {e.errors()[0]['msg']}")
    
    # Note too long
    try:
        RecognizeRequest(receiver_id=2, credits=10, note="A" * 501)
        print("✗ Should have failed with note too long")
    except ValidationError as e:
        print(f"✓ Correctly rejected note too long: {e.errors()[0]['msg']}")

def test_redeem_validation():
    print("\n=== Testing RedeemRequest Validation ===")
    
    # Valid redemption
    try:
        valid = RedeemRequest(credits=100)
        print(f"✓ Valid redemption: {valid.credits} credits")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Invalid credits (0)
    try:
        RedeemRequest(credits=0)
        print("✗ Should have failed with credits = 0")
    except ValidationError as e:
        print(f"✓ Correctly rejected credits = 0: {e.errors()[0]['msg']}")
    
    # Invalid credits (> 10000)
    try:
        RedeemRequest(credits=10001)
        print("✗ Should have failed with credits > 10000")
    except ValidationError as e:
        print(f"✓ Correctly rejected credits > 10000: {e.errors()[0]['msg']}")

if __name__ == "__main__":
    print("Testing Pydantic Validation for all request models...")
    test_create_user_validation()
    test_recognize_validation()
    test_redeem_validation()
    print("\n✓ All validation tests completed!")
