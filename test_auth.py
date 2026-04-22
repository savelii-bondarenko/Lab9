import pytest
from auth import authenticate_user

# ── Statement / Branch / Condition / MC/DC / Path Coverage ──────────────────

# Path 1: username or password is empty
def test_missing_credentials_empty_username():
    """Statement✓ Branch✓ Condition(A=T)✓"""
    db = {}
    assert authenticate_user("", "pass", db) == "Missing credentials"

def test_missing_credentials_empty_password():
    """Statement✓ Branch✓ Condition(B=T)✓"""
    db = {}
    assert authenticate_user("user", "", db) == "Missing credentials"

def test_missing_credentials_both_empty():
    """Condition combination (A=T, B=T)"""
    db = {}
    assert authenticate_user("", "", db) == "Missing credentials"

# Path 2: username not in db
def test_user_not_found():
    """Statement✓ Branch✓"""
    db = {}
    assert authenticate_user("user", "pass", db) == "User not found"

# Path 3: account locked (attempts >= 3)
def test_account_locked():
    """Statement✓ Branch✓"""
    db = {"user": {"password": "pass", "attempts": 3}}
    assert authenticate_user("user", "pass", db) == "Account locked"

def test_account_locked_boundary():
    """Boundary: attempts == 3 (exactly)"""
    db = {"user": {"password": "pass", "attempts": 3}}
    assert authenticate_user("user", "pass", db) == "Account locked"

def test_account_not_locked_boundary():
    """Boundary: attempts == 2 (just below lock), wrong password → Invalid password"""
    db = {"user": {"password": "correct", "attempts": 2}}
    assert authenticate_user("user", "wrong", db) == "Invalid password"

# Path 4: invalid password – attempts incremented
def test_invalid_password():
    """Statement✓ Branch✓ Data-flow: attempts def→use"""
    db = {"user": {"password": "pass", "attempts": 0}}
    assert authenticate_user("user", "wrong", db) == "Invalid password"
    assert db["user"]["attempts"] == 1

def test_invalid_password_no_prior_attempts_key():
    """Branch: attempts key missing → defaults to 0"""
    db = {"user": {"password": "pass"}}
    assert authenticate_user("user", "wrong", db) == "Invalid password"
    assert db["user"]["attempts"] == 1

# Path 5: successful authentication
def test_success():
    """Statement✓ Branch✓ Data-flow: attempts reset"""
    db = {"user": {"password": "pass", "attempts": 1}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0

def test_success_no_prior_attempts():
    """Success without prior attempts key"""
    db = {"user": {"password": "pass"}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0

# ── MC/DC specific (one condition flipped at a time) ────────────────────────

def test_mcdc_username_none():
    """MC/DC: only username falsy"""
    db = {}
    assert authenticate_user(None, "pass", db) == "Missing credentials"

def test_mcdc_password_none():
    """MC/DC: only password falsy"""
    db = {}
    assert authenticate_user("user", None, db) == "Missing credentials"

def test_mcdc_both_present():
    """MC/DC: both truthy → proceed past first check"""
    db = {}
    assert authenticate_user("user", "pass", db) == "User not found"
