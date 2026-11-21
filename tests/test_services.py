"""
Unit tests for SheCycle services:
- Revenue split sums to exactly 100%
- Status transition lifecycle logic
- Registration ID, mobile, and PIN validators
- Data masking for privacy
- Scrap rate & earnings calculations
"""

import pytest
import sys
import os

# Add scratch/shecycle to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import (
    validate_reg_id,
    validate_indian_mobile,
    validate_pin,
    validate_positive_weight,
    mask_phone,
    mask_bank_account,
    hash_pin,
    verify_pin,
    is_valid_transition,
    get_next_status,
    verify_revenue_split,
    calculate_earnings,
    REVENUE_SPLIT,
    SCRAP_RATES,
    calculate_environmental_impact
)


def test_revenue_split_sums_to_100_percent():
    """Verify statutory revenue split precisely equals 1.0 (100%)."""
    total = sum(REVENUE_SPLIT.values())
    assert abs(total - 1.0) < 1e-6
    assert verify_revenue_split() is True
    assert REVENUE_SPLIT["shg"] == 0.75
    assert REVENUE_SPLIT["logistics"] == 0.12
    assert REVENUE_SPLIT["platform"] == 0.08
    assert REVENUE_SPLIT["green_credits"] == 0.05


def test_earnings_calculation():
    """Verify earnings calculation and penny reconciliation."""
    res = calculate_earnings("Smartphones & Feature Phones", 10.0)
    assert res["rate_per_kg"] == 120.0
    assert res["gross_value"] == 1200.0
    assert res["shg_amount"] == 900.0          # 75%
    assert res["logistics_amount"] == 144.0     # 12%
    assert res["platform_amount"] == 96.0       # 8%
    assert res["green_credits_fund"] == 60.0    # 5%
    # Sum of parts must exactly match gross
    assert round(res["shg_amount"] + res["logistics_amount"] + res["platform_amount"] + res["green_credits_fund"], 2) == res["gross_value"]


def test_status_transitions():
    """Test valid and invalid status transitions."""
    # Valid forward sequence
    assert is_valid_transition("Requested", "Assigned") is True
    assert is_valid_transition("Assigned", "Collected") is True
    assert is_valid_transition("Collected", "Sorted") is True
    assert is_valid_transition("Sorted", "Delivered to Recycler") is True
    assert is_valid_transition("Delivered to Recycler", "Settled") is True

    # Invalid transitions
    assert is_valid_transition("Requested", "Settled") is False
    assert is_valid_transition("Settled", "Requested") is False
    assert is_valid_transition("Collected", "Delivered to Recycler") is False

    # Happy path helper
    assert get_next_status("Requested") == "Assigned"
    assert get_next_status("Settled") is None


def test_reg_id_validation():
    """Test NULM and NRLM regex pattern matching."""
    # Valid formats
    valid, cid = validate_reg_id("NULM-2024-88")
    assert valid is True
    assert cid == "NULM-2024-88"

    valid, cid = validate_reg_id("nulm-2023-104")
    assert valid is True
    assert cid == "NULM-2023-104"

    valid, cid = validate_reg_id("NRLM-1024")
    assert valid is True
    assert cid == "NRLM-1024"

    # Invalid formats
    assert validate_reg_id("")[0] is False
    assert validate_reg_id("RANDOM-123")[0] is False
    assert validate_reg_id("NULM-ABC-12")[0] is False
    assert validate_reg_id("SHG-001")[0] is False


def test_mobile_validation():
    """Test Indian 10-digit mobile number rules."""
    # Valid
    assert validate_indian_mobile("9876543210")[0] is True
    assert validate_indian_mobile("+91 9876543210")[0] is True
    assert validate_indian_mobile("09876543210")[0] is True
    assert validate_indian_mobile("8123456789")[1] == "8123456789"

    # Invalid
    assert validate_indian_mobile("1234567890")[0] is False  # starts with 1
    assert validate_indian_mobile("98765")[0] is False       # too short
    assert validate_indian_mobile("abcdefghij")[0] is False  # non-numeric


def test_pin_and_auth():
    """Test 4-digit PIN validator and salted hashing."""
    assert validate_pin("1234")[0] is True
    assert validate_pin("123")[0] is False
    assert validate_pin("abcd")[0] is False

    pin_hash, salt = hash_pin("1234")
    assert verify_pin("1234", salt, pin_hash) is True
    assert verify_pin("0000", salt, pin_hash) is False


def test_data_masking():
    """Test privacy masking for DPDP Act compliance."""
    assert mask_phone("9876543210") == "98XXXXXX10"
    assert mask_phone("") == "N/A"
    assert mask_bank_account("987654321234") == "****1234"
    assert mask_bank_account("") == "****0000"


def test_weight_validator():
    """Test numeric weight parsing."""
    valid, w, msg = validate_positive_weight(2.5)
    assert valid is True and w == 2.5

    valid, w, msg = validate_positive_weight("4.8")
    assert valid is True and w == 4.8

    assert validate_positive_weight(-1)[0] is False
    assert validate_positive_weight("abc")[0] is False
    assert validate_positive_weight(1000)[0] is False


def test_environmental_impact():
    """Test CO2 and toxic diverted calculation."""
    impact = calculate_environmental_impact(100.0)
    assert impact["co2_avoided_kg"] == 144.0
    assert impact["heavy_metals_prevented_g"] == 2800.0
    assert impact["trees_equivalent"] > 0
