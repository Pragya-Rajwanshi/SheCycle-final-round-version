"""
services.py - Core Business Logic for SheCycle
Handles:
- Status lifecycle state machine & transitions
- Scrutiny and regex validation (NRLM/NULM, mobile numbers, PINs)
- Illustrative scrap rate calculation and strict revenue split (summing to 100%)
- Masking utilities for citizen and SHG privacy (DPDP Act 2023 alignment)
- Impact estimation (CO2 avoided, toxic leakage diverted)
"""

import re
import hashlib
import secrets
from typing import Dict, Any, Tuple, Optional, List

# Allowed Status Pipeline
STATUS_ORDER = [
    "Requested",
    "Assigned",
    "Collected",
    "Sorted",
    "Delivered to Recycler",
    "Settled"
]

STATUS_TRANSITIONS = {
    "Requested": ["Assigned", "Cancelled"],
    "Assigned": ["Collected", "Requested"],  # Can revert if unassigned
    "Collected": ["Sorted"],
    "Sorted": ["Delivered to Recycler"],
    "Delivered to Recycler": ["Settled"],
    "Settled": [],
    "Cancelled": []
}

# Revenue Split Configuration (Strictly sums to 100%)
# SHG 75%, Logistics & Safety Fund 12%, Platform 8%, Green Credits Fund 5%
REVENUE_SPLIT = {
    "shg": 0.75,
    "logistics": 0.12,
    "platform": 0.08,
    "green_credits": 0.05
}

# Illustrative Demo Scrap Rates (Clearly labelled in UI as demo rates)
SCRAP_RATES: Dict[str, Dict[str, Any]] = {
    "Smartphones & Feature Phones": {
        "rate_per_kg": 120.0,
        "green_credits_per_kg": 25,
        "co2_factor": 1.85,  # kg CO2e avoided per kg
        "desc": "Intact or damaged smartphones, printed circuit boards, screens"
    },
    "Laptops & Computing Parts": {
        "rate_per_kg": 95.0,
        "green_credits_per_kg": 20,
        "co2_factor": 1.60,
        "desc": "Motherboards, RAM, laptop bodies, processors, cables"
    },
    "Lithium Batteries & Chargers": {
        "rate_per_kg": 150.0,
        "green_credits_per_kg": 30,
        "co2_factor": 2.10,
        "desc": "Critical hazardous fraction: must be kept sealed and handed over unopened"
    },
    "Small Home Appliances": {
        "rate_per_kg": 45.0,
        "green_credits_per_kg": 10,
        "co2_factor": 1.10,
        "desc": "Electric irons, toasters, kettles, blenders, fans"
    },
    "Mixed E-Scrap": {
        "rate_per_kg": 55.0,
        "green_credits_per_kg": 12,
        "co2_factor": 1.30,
        "desc": "Assorted wiring, connectors, adapters, remotes, mixed electronics"
    }
}

# Approved Meerut Localities / Wards
MEERUT_WARDS = [
    "Kankar Khera",
    "Shastri Nagar",
    "Rohta Road",
    "Begum Bridge",
    "Modipuram",
    "Partapur",
    "Pallavpuram",
    "Civil Lines",
    "Sadar Bazar",
    "Suraj Kund"
]

# Authorised Recyclers in UP / NCR Hub
AUTHORISED_RECYCLERS = [
    "Attero Recycling Pvt Ltd (CPCB/UPPCB Reg #CPCB-EW-042)",
    "Greentek Remanufacturers Pvt Ltd (Greater Noida/Meerut Hub #UPPCB-881)",
    "Eco-Birad E-Waste Solutions (Meerut Municipal Cluster Auth #MR-09)",
    "Clean-E Green Systems CPCB Authorized Facility (#CPCB-NCR-31)"
]


# ==========================================
# 1. VALIDATION FUNCTIONS
# ==========================================

def validate_reg_id(reg_id: str) -> Tuple[bool, str]:
    """
    Validates SHG registration ID format.
    Accepts NULM-YYYY-NN (or NN..) and NRLM-NNNN (4-6 digits).
    Example: NULM-2024-88, NRLM-1024, NULM-2023-104.
    """
    if not reg_id:
        return False, "Registration ID cannot be empty."
    
    clean_id = reg_id.strip().upper()
    pattern = r"^(NULM-\d{4}-\d{2,4}|NRLM-\d{4,6})$"
    if not re.match(pattern, clean_id):
        return False, "Invalid format. Expected NULM-YYYY-NN (e.g., NULM-2024-88) or NRLM-NNNN (e.g., NRLM-1024)."
    
    return True, clean_id


def validate_indian_mobile(phone: str) -> Tuple[bool, str]:
    """
    Validates 10-digit Indian mobile number starting with 6, 7, 8, or 9.
    Strips spaces, +91, or leading 0.
    """
    if not phone:
        return False, "Mobile number is required."
    
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("0"):
        cleaned = cleaned[1:]
    
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        return False, "Must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9."
    
    return True, cleaned


def validate_pin(pin: str) -> Tuple[bool, str]:
    """Validates simple 4-digit demo PIN."""
    if not pin or not re.match(r"^\d{4}$", pin.strip()):
        return False, "PIN must be exactly 4 digits (e.g. 1234)."
    return True, pin.strip()


def validate_positive_weight(weight: Any) -> Tuple[bool, float, str]:
    """Ensures weight is a positive float."""
    try:
        w = float(weight)
        if w <= 0:
            return False, 0.0, "Weight must be greater than 0 kg."
        if w > 500:
            return False, 0.0, "For residential pickups, weight cannot exceed 500 kg per request."
        return True, round(w, 2), ""
    except (ValueError, TypeError):
        return False, 0.0, "Weight must be a valid numeric value in kilograms."


# ==========================================
# 2. PRIVACY & MASKING UTILITIES (DPDP Act)
# ==========================================

def mask_phone(phone: str) -> str:
    """Masks 10-digit phone number as 98XXXXXX10."""
    if not phone:
        return "N/A"
    cleaned = re.sub(r"\D", "", phone)
    if len(cleaned) == 10:
        return f"{cleaned[:2]}XXXXXX{cleaned[-2:]}"
    if len(cleaned) > 4:
        return f"{cleaned[:2]}...{cleaned[-2:]}"
    return "****"


def mask_bank_account(account: str) -> str:
    """Masks bank account number as ****1234."""
    if not account:
        return "****0000"
    cleaned = account.strip()
    if len(cleaned) >= 4:
        return f"****{cleaned[-4:]}"
    return "****"


# ==========================================
# 3. AUTHENTICATION & PIN SECURITY
# ==========================================

def hash_pin(pin: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a PIN with a salt using SHA-256."""
    if not salt:
        salt = secrets.token_hex(8)
    salted = f"{salt}:{pin}".encode("utf-8")
    pin_hash = hashlib.sha256(salted).hexdigest()
    return pin_hash, salt


def verify_pin(pin: str, salt: str, expected_hash: str) -> bool:
    """Verifies PIN against stored salt and hash."""
    test_hash, _ = hash_pin(pin, salt)
    return secrets.compare_digest(test_hash, expected_hash)


# ==========================================
# 4. STATUS TRANSITIONS & LIFECYCLE
# ==========================================

def is_valid_transition(current_status: str, new_status: str) -> bool:
    """Checks if a transition from current_status to new_status is valid."""
    allowed = STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def get_next_status(current_status: str) -> Optional[str]:
    """Returns standard happy-path next status."""
    try:
        idx = STATUS_ORDER.index(current_status)
        if idx + 1 < len(STATUS_ORDER):
            return STATUS_ORDER[idx + 1]
    except ValueError:
        pass
    return None


# ==========================================
# 5. FINANCIAL CALCULATIONS & EARNINGS SPLIT
# ==========================================

def verify_revenue_split() -> bool:
    """Verifies that all revenue split percentages strictly sum to 100%."""
    total = sum(REVENUE_SPLIT.values())
    return abs(total - 1.0) < 1e-6


def calculate_earnings(category: str, weight_kg: float) -> Dict[str, Any]:
    """
    Computes illustrative scrap earnings and statutory split.
    Split: SHG 75%, Logistics 12%, Platform 8%, Green Credits Fund 5%.
    """
    if not verify_revenue_split():
        raise ValueError("Revenue split percentages must sum exactly to 100%.")

    cat_info = SCRAP_RATES.get(category, SCRAP_RATES["Mixed E-Scrap"])
    rate_per_kg = cat_info["rate_per_kg"]
    
    gross_value = round(weight_kg * rate_per_kg, 2)
    shg_amount = round(gross_value * REVENUE_SPLIT["shg"], 2)
    logistics_amount = round(gross_value * REVENUE_SPLIT["logistics"], 2)
    platform_amount = round(gross_value * REVENUE_SPLIT["platform"], 2)
    # Ensure remainder goes to green credits fund to prevent penny rounding mismatch
    green_credits_fund = round(gross_value - (shg_amount + logistics_amount + platform_amount), 2)
    
    # Citizen green credits points
    points_per_kg = cat_info.get("green_credits_per_kg", 10)
    citizen_credits = int(round(weight_kg * points_per_kg))

    # Impact metric
    co2_factor = cat_info.get("co2_factor", 1.44)
    co2_avoided_kg = round(weight_kg * co2_factor, 2)

    return {
        "category": category,
        "rate_per_kg": rate_per_kg,
        "weight_kg": weight_kg,
        "gross_value": gross_value,
        "shg_amount": shg_amount,
        "logistics_amount": logistics_amount,
        "platform_amount": platform_amount,
        "green_credits_fund": green_credits_fund,
        "citizen_credits": citizen_credits,
        "co2_avoided_kg": co2_avoided_kg,
        "split_ratios": REVENUE_SPLIT
    }


# ==========================================
# 6. ENVIRONMENTAL IMPACT ESTIMATES
# ==========================================

def calculate_environmental_impact(total_kg: float) -> Dict[str, Any]:
    """
    Returns estimated environmental savings based on UNEP/CPCB lifecycle averages.
    Clearly labelled in UI as illustrative estimates with stated assumptions:
    - ~1.44 kg CO2e avoided per 1 kg e-waste diverted from open burning/landfill
    - ~28g lead/toxic heavy metal contamination prevented per kg
    - ~45 liters water contamination prevented per kg
    """
    co2_saved = round(total_kg * 1.44, 1)
    heavy_metals_g = round(total_kg * 28.0, 1)
    water_saved_l = round(total_kg * 45.0, 1)
    trees_equivalent = round(co2_saved / 21.0, 1)  # 1 mature tree absorbs ~21 kg CO2/yr

    return {
        "co2_avoided_kg": co2_saved,
        "heavy_metals_prevented_g": heavy_metals_g,
        "water_protected_liters": water_saved_l,
        "trees_equivalent": trees_equivalent,
        "disclaimer": "Estimates based on CPCB & UNEP lifecycle benchmarks (1.44 kg CO2e / kg e-waste diverted from unscientific burning)."
    }
