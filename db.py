"""
db.py - SQLite Database Layer for SheCycle
Handles:
- Schema initialization and migrations
- High-fidelity realistic seed data (3 Approved SHGs, 1 Pending SHG, 28 requests across 60 days)
- Complete audit trail logging (status_history table)
- Parameterised SQL queries with connection management
- Sequential EW-00001 style ID generation
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shecycle.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force_reseed: bool = False) -> None:
    """Initializes tables and seeds data if empty or forced."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS admin_audit;")
        cursor.execute("DROP TABLE IF EXISTS status_history;")
        cursor.execute("DROP TABLE IF EXISTS requests;")
        cursor.execute("DROP TABLE IF EXISTS shgs;")

    # 1. SHG Partners Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shgs (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        portal_type TEXT NOT NULL,
        reg_id TEXT UNIQUE NOT NULL,
        leader_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        localities TEXT NOT NULL,
        bank_ac_masked TEXT NOT NULL,
        pin_hash TEXT NOT NULL,
        pin_salt TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending Approval',
        rejection_reason TEXT,
        approved_at TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. E-Waste Pickup Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        seq_num INTEGER UNIQUE,
        citizen_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        phone_last4 TEXT NOT NULL,
        address TEXT NOT NULL,
        ward TEXT NOT NULL,
        category TEXT NOT NULL,
        estimated_kg REAL NOT NULL,
        actual_kg REAL,
        pickup_slot TEXT NOT NULL,
        photo_name TEXT,
        status TEXT NOT NULL DEFAULT 'Requested',
        assigned_shg_id TEXT,
        assigned_shg_name TEXT,
        gross_value REAL DEFAULT 0.0,
        shg_earnings REAL DEFAULT 0.0,
        logistics_fund REAL DEFAULT 0.0,
        platform_fee REAL DEFAULT 0.0,
        green_credit_fund REAL DEFAULT 0.0,
        green_credits_citizen INTEGER DEFAULT 0,
        safety_checklist_passed INTEGER DEFAULT 0,
        recycler_name TEXT,
        recycler_challan_no TEXT,
        sorting_breakdown TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (assigned_shg_id) REFERENCES shgs(id)
    );
    """)

    # 3. Status History (Immutable Compliance Audit Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT NOT NULL,
        actor TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY (request_id) REFERENCES requests(id)
    );
    """)

    # 4. Admin Audit Log (For SHG verifications, overrides)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target_id TEXT NOT NULL,
        details TEXT NOT NULL,
        actor TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM shgs;")
    shg_count = cursor.fetchone()[0]

    if shg_count == 0 or force_reseed:
        _seed_demo_data(conn)

    conn.close()


def _seed_demo_data(conn: sqlite3.Connection) -> None:
    """Populates realistic demo dataset for the Meerut, UP pilot."""
    from services import hash_pin, calculate_earnings, SCRAP_RATES

    cursor = conn.cursor()
    now = datetime.now()

    # Default PIN: 1234 for all seeded SHGs
    pin_hash_1234, salt_1234 = hash_pin("1234")

    # 1. Seed SHGs (3 Approved, 1 Pending)
    shg_data = [
        (
            "SHG-001",
            "Maa Durga Mahila SHG",
            "DAY-NULM (Urban)",
            "NULM-2024-88",
            "Sunita Devi",
            "9837112233",
            "Kankar Khera, Modipuram, Pallavpuram",
            "****1234",
            pin_hash_1234,
            salt_1234,
            "Approved",
            None,
            (now - timedelta(days=65)).strftime("%Y-%m-%d %H:%M:%S"),
            "Municipal Commissioner, Meerut",
            (now - timedelta(days=67)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            "SHG-002",
            "Ekta Sakhi Mahila SHG",
            "DAY-NRLM (Rural)",
            "NRLM-1024",
            "Geeta Rani",
            "9897223344",
            "Rohta Road, Partapur",
            "****5678",
            pin_hash_1234,
            salt_1234,
            "Approved",
            None,
            (now - timedelta(days=50)).strftime("%Y-%m-%d %H:%M:%S"),
            "District Development Officer (DDO), Meerut",
            (now - timedelta(days=52)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            "SHG-003",
            "Pragati Mahila Swavlambi Samuh",
            "DAY-NULM (Urban)",
            "NULM-2023-45",
            "Shabana Parveen",
            "9812334455",
            "Shastri Nagar, Begum Bridge, Civil Lines, Sadar Bazar, Suraj Kund",
            "****9012",
            pin_hash_1234,
            salt_1234,
            "Approved",
            None,
            (now - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S"),
            "City Project Officer (NULM), Meerut",
            (now - timedelta(days=42)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            "SHG-004",
            "Nav Chetna Mahila Mandal",
            "DAY-NULM (Urban)",
            "NULM-2025-12",
            "Anita Tomar",
            "9876554433",
            "Shastri Nagar, Suraj Kund",
            "****4321",
            pin_hash_1234,
            salt_1234,
            "Pending Approval",
            None,
            None,
            None,
            (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        )
    ]

    cursor.executemany("""
    INSERT INTO shgs (
        id, name, portal_type, reg_id, leader_name, phone, localities,
        bank_ac_masked, pin_hash, pin_salt, status, rejection_reason,
        approved_at, approved_by, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, shg_data)

    # 2. Seed 28 Requests across 60 days
    citizens = [
        ("Rahul Sharma", "9876543210", "House 42, Pocket B, Kankar Khera", "Kankar Khera"),
        ("Pooja Verma", "9812345678", "Flat 302, Green Enclave, Shastri Nagar", "Shastri Nagar"),
        ("Amit Kumar", "9123456789", "Near Primary School, Rohta Road", "Rohta Road"),
        ("Dr. Rajesh Gupta", "9927012345", "12-A, Civil Lines, Near Circuit House", "Civil Lines"),
        ("Suresh Tyagi", "9837098765", "Modipuram Crossing, NH-58", "Modipuram"),
        ("Meena Agarwal", "9756123456", "Main Market, Begum Bridge", "Begum Bridge"),
        ("Vikram Singh", "9412098765", "Plot 18, Phase 1, Partapur Industrial Area", "Partapur"),
        ("Kavita Devi", "9897123987", "Sector 3, Pallavpuram", "Pallavpuram"),
        ("Manoj Chauhan", "9837564738", "Sadar Bazar Cantt, Near Clock Tower", "Sadar Bazar"),
        ("Anurag Dixit", "9917234567", "Suraj Kund Sports Market Lane", "Suraj Kund"),
        ("Sunil Mittal", "9812001122", "Defence Colony, Kankar Khera", "Kankar Khera"),
        ("Deepak Rathi", "9823445566", "Shivaji Road, Rohta Road", "Rohta Road"),
        ("Neha Saxena", "9837998877", "Block 4, Shastri Nagar", "Shastri Nagar"),
        ("Alok Rastogi", "9456778899", "Budhana Gate, Sadar Area", "Sadar Bazar"),
        ("Ritu Goel", "9897001144", "Saket, Near Begum Bridge", "Begum Bridge"),
        ("Harish Chawla", "9812776655", "Pallavpuram Phase 2", "Pallavpuram"),
        ("Dinesh Chandra", "9760889900", "Partapur By-pass Colony", "Partapur"),
        ("Priyanka Jain", "9837443322", "Civil Lines Police Line Road", "Civil Lines"),
        ("Gaurav Tomar", "9927665544", "Modipuram Agriculture University Road", "Modipuram"),
        ("Tarun Bali", "9812889933", "Suraj Kund Road, Opp Lake", "Suraj Kund"),
        ("Rohit Rawat", "9876112233", "Kankar Khera Bypass", "Kankar Khera"),
        ("Preeti Mishra", "9837332211", "Central Market, Shastri Nagar", "Shastri Nagar"),
        ("Naveen Kashyap", "9897887766", "Rohta Road Canal Colony", "Rohta Road"),
        ("Rashmi Bhardwaj", "9412554433", "Begum Bridge Road", "Begum Bridge"),
        ("Kamal Nayan", "9837009988", "Shastri Nagar Sector 6", "Shastri Nagar"),
        ("Vandana Sharma", "9917443322", "Civil Lines Court Road", "Civil Lines"),
        ("Sanjay Singhal", "9812332211", "Modipuram Greens", "Modipuram"),
        ("Monika Bansal", "9756009911", "Pallavpuram Main Road", "Pallavpuram")
    ]

    categories = list(SCRAP_RATES.keys())
    slots = ["Morning (9 AM - 12 PM)", "Afternoon (1 PM - 4 PM)", "Evening (4 PM - 7 PM)", "Weekend Special"]
    recyclers = [
        "Attero Recycling Pvt Ltd (CPCB/UPPCB Reg #CPCB-EW-042)",
        "Greentek Remanufacturers Pvt Ltd (Greater Noida/Meerut Hub #UPPCB-881)",
        "Eco-Birad E-Waste Solutions (Meerut Municipal Cluster Auth #MR-09)"
    ]

    # Pre-calculated distribution of statuses:
    # 4 Requested, 5 Assigned, 5 Collected, 5 Sorted, 5 Delivered to Recycler, 4 Settled = 28
    status_distribution = (
        ["Requested"] * 4 +
        ["Assigned"] * 5 +
        ["Collected"] * 5 +
        ["Sorted"] * 5 +
        ["Delivered to Recycler"] * 5 +
        ["Settled"] * 4
    )

    # SHG mapping based on locality
    shg_locality_map = {
        "Kankar Khera": ("SHG-001", "Maa Durga Mahila SHG"),
        "Modipuram": ("SHG-001", "Maa Durga Mahila SHG"),
        "Pallavpuram": ("SHG-001", "Maa Durga Mahila SHG"),
        "Rohta Road": ("SHG-002", "Ekta Sakhi Mahila SHG"),
        "Partapur": ("SHG-002", "Ekta Sakhi Mahila SHG"),
        "Shastri Nagar": ("SHG-003", "Pragati Mahila Swavlambi Samuh"),
        "Begum Bridge": ("SHG-003", "Pragati Mahila Swavlambi Samuh"),
        "Civil Lines": ("SHG-003", "Pragati Mahila Swavlambi Samuh"),
        "Sadar Bazar": ("SHG-003", "Pragati Mahila Swavlambi Samuh"),
        "Suraj Kund": ("SHG-003", "Pragati Mahila Swavlambi Samuh"),
    }

    for idx, (name, phone, address, ward) in enumerate(citizens, start=1):
        req_id = f"EW-{idx:05d}"
        status = status_distribution[idx - 1]
        category = categories[(idx - 1) % len(categories)]
        slot = slots[(idx - 1) % len(slots)]
        phone_last4 = phone[-4:]

        # Create realistic timestamp spread over the last 60 days
        # Oldest requests are settled; newest are requested
        if status == "Settled":
            days_ago = random.randint(40, 58)
        elif status == "Delivered to Recycler":
            days_ago = random.randint(25, 39)
        elif status == "Sorted":
            days_ago = random.randint(15, 24)
        elif status == "Collected":
            days_ago = random.randint(7, 14)
        elif status == "Assigned":
            days_ago = random.randint(2, 6)
        else:  # Requested
            # Make request 1 unassigned for > 48 hours to trigger exception alert!
            days_ago = 3 if idx == 1 else random.randint(0, 2)

        req_time = now - timedelta(days=days_ago, hours=random.randint(1, 10))
        created_at_str = req_time.strftime("%Y-%m-%d %H:%M:%S")

        estimated_kg = round(random.uniform(1.2, 8.5), 1)
        actual_kg = None
        assigned_shg_id = None
        assigned_shg_name = None
        gross_val = 0.0
        shg_earn = 0.0
        logistics_fund = 0.0
        plat_fee = 0.0
        gc_fund = 0.0
        gc_citizen = 0
        safety_passed = 0
        recycler_name = None
        recycler_challan = None
        sorting_json = None

        history_events = [
            (req_id, None, "Requested", f"Citizen: {name}", created_at_str, "Pickup requested via citizen web portal.")
        ]

        if status != "Requested":
            shg_id, shg_name = shg_locality_map.get(ward, ("SHG-001", "Maa Durga Mahila SHG"))
            assigned_shg_id = shg_id
            assigned_shg_name = shg_name
            t_assigned = req_time + timedelta(hours=random.randint(2, 8))
            history_events.append(
                (req_id, "Requested", "Assigned", f"SHG: {shg_name}", t_assigned.strftime("%Y-%m-%d %H:%M:%S"), f"Pickup accepted by {shg_name}.")
            )

        if status in ["Collected", "Sorted", "Delivered to Recycler", "Settled"]:
            actual_kg = round(estimated_kg + random.uniform(-0.3, 0.4), 2)
            if actual_kg <= 0.2:
                actual_kg = 0.5
            safety_passed = 1
            earnings = calculate_earnings(category, actual_kg)
            gross_val = earnings["gross_value"]
            shg_earn = earnings["shg_amount"]
            logistics_fund = earnings["logistics_amount"]
            plat_fee = earnings["platform_amount"]
            gc_fund = earnings["green_credits_fund"]
            gc_citizen = earnings["citizen_credits"]

            t_collected = req_time + timedelta(hours=random.randint(10, 24))
            history_events.append(
                (req_id, "Assigned", "Collected", f"SHG: {assigned_shg_name}", t_collected.strftime("%Y-%m-%d %H:%M:%S"),
                 f"Doorstep collection completed. Actual weight verified: {actual_kg} kg. Safety checklist verified.")
            )

        if status in ["Sorted", "Delivered to Recycler", "Settled"]:
            # Sorting fractions
            metal_fraction = round(actual_kg * 0.40, 2)
            pcb_fraction = round(actual_kg * 0.25, 2)
            battery_fraction = round(actual_kg * 0.15, 2)
            plastic_fraction = round(actual_kg * 0.15, 2)
            other_fraction = round(actual_kg - (metal_fraction + pcb_fraction + battery_fraction + plastic_fraction), 2)
            sorting_json = json.dumps({
                "metals_kg": metal_fraction,
                "circuit_boards_kg": pcb_fraction,
                "lithium_batteries_kg": battery_fraction,
                "plastics_kg": plastic_fraction,
                "other_kg": max(0.0, other_fraction)
            })
            t_sorted = req_time + timedelta(hours=random.randint(26, 36))
            history_events.append(
                (req_id, "Collected", "Sorted", f"SHG: {assigned_shg_name}", t_sorted.strftime("%Y-%m-%d %H:%M:%S"),
                 "Basic segregation into fractions completed. Lithium batteries kept sealed.")
            )

        if status in ["Delivered to Recycler", "Settled"]:
            recycler_name = recyclers[(idx - 1) % len(recyclers)]
            recycler_challan = f"REC-UP-2026-{1000 + idx}"
            t_delivered = req_time + timedelta(hours=random.randint(40, 52))
            history_events.append(
                (req_id, "Sorted", "Delivered to Recycler", f"SHG: {assigned_shg_name}", t_delivered.strftime("%Y-%m-%d %H:%M:%S"),
                 f"Handed over to authorized recycler: {recycler_name}. Challan #{recycler_challan}.")
            )

        if status == "Settled":
            t_settled = req_time + timedelta(hours=random.randint(56, 72))
            history_events.append(
                (req_id, "Delivered to Recycler", "Settled", "Admin: Municipal Finance Dept", t_settled.strftime("%Y-%m-%d %H:%M:%S"),
                 f"Recycler payout verified. SHG share ₹{shg_earn:.2f} credited to DBT account.")
            )

        updated_at_str = history_events[-1][4]

        cursor.execute("""
        INSERT INTO requests (
            id, seq_num, citizen_name, phone, phone_last4, address, ward,
            category, estimated_kg, actual_kg, pickup_slot, photo_name,
            status, assigned_shg_id, assigned_shg_name, gross_value,
            shg_earnings, logistics_fund, platform_fee, green_credit_fund,
            green_credits_citizen, safety_checklist_passed, recycler_name,
            recycler_challan_no, sorting_breakdown, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            req_id, idx, name, phone, phone_last4, address, ward,
            category, estimated_kg, actual_kg, slot, None,
            status, assigned_shg_id, assigned_shg_name, gross_val,
            shg_earn, logistics_fund, plat_fee, gc_fund,
            gc_citizen, safety_passed, recycler_name,
            recycler_challan, sorting_json, created_at_str, updated_at_str
        ))

        for ev in history_events:
            cursor.execute("""
            INSERT INTO status_history (
                request_id, from_status, to_status, actor, timestamp, note
            ) VALUES (?, ?, ?, ?, ?, ?);
            """, ev)

    # 3. Seed initial admin audit entry
    cursor.execute("""
    INSERT INTO admin_audit (action, target_id, details, actor, timestamp)
    VALUES (?, ?, ?, ?, ?);
    """, (
        "SYSTEM_INITIALIZE",
        "SYSTEM",
        "Initial Meerut E-Waste Pilot Dataset successfully seeded.",
        "System Admin",
        now.strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()


# ==========================================
# QUERY & MUTATION APIS
# ==========================================

def get_next_request_id(conn: sqlite3.Connection) -> Tuple[str, int]:
    """Generates sequential EW-00001 style request ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(seq_num), 0) + 1 FROM requests;")
    seq = cursor.fetchone()[0]
    req_id = f"EW-{seq:05d}"
    return req_id, seq


def create_pickup_request(
    citizen_name: str,
    phone: str,
    address: str,
    ward: str,
    category: str,
    estimated_kg: float,
    pickup_slot: str,
    photo_name: Optional[str] = None
) -> Tuple[str, int]:
    """Creates a new pickup request and initial status history."""
    from services import calculate_earnings

    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    req_id, seq = get_next_request_id(conn)
    phone_last4 = phone[-4:] if len(phone) >= 4 else phone

    # Calculate initial provisional credits based on estimated weight
    earnings = calculate_earnings(category, estimated_kg)
    provisional_credits = earnings["citizen_credits"]

    cursor.execute("""
    INSERT INTO requests (
        id, seq_num, citizen_name, phone, phone_last4, address, ward,
        category, estimated_kg, pickup_slot, photo_name, status,
        green_credits_citizen, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Requested', ?, ?, ?);
    """, (
        req_id, seq, citizen_name, phone, phone_last4, address, ward,
        category, estimated_kg, pickup_slot, photo_name,
        provisional_credits, now_str, now_str
    ))

    cursor.execute("""
    INSERT INTO status_history (
        request_id, from_status, to_status, actor, timestamp, note
    ) VALUES (?, NULL, 'Requested', ?, ?, 'Doorstep pickup requested by citizen.');
    """, (req_id, f"Citizen: {citizen_name}", now_str))

    conn.commit()
    conn.close()
    return req_id, provisional_credits


def get_request_by_id(req_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a request by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE id = ?;", (req_id.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def track_request(req_id: str, phone_last4: str) -> Optional[Dict[str, Any]]:
    """Secured tracking query: requires request ID + last 4 digits of phone."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM requests
    WHERE id = ? AND phone_last4 = ?;
    """, (req_id.strip().upper(), phone_last4.strip()))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_request_history(req_id: str) -> List[Dict[str, Any]]:
    """Fetches audit trail status history for a request."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM status_history
    WHERE request_id = ?
    ORDER BY id ASC;
    """, (req_id.strip().upper(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_shg_by_id(shg_id: str) -> Optional[Dict[str, Any]]:
    """Fetches an SHG by primary ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shgs WHERE id = ?;", (shg_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_shg_by_reg_id(reg_id: str) -> Optional[Dict[str, Any]]:
    """Fetches an SHG by Govt Registration ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shgs WHERE UPPER(reg_id) = ?;", (reg_id.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def register_shg(
    name: str,
    portal_type: str,
    reg_id: str,
    leader_name: str,
    phone: str,
    localities_list: List[str],
    bank_ac: str,
    pin: str
) -> Tuple[bool, str, Optional[str]]:
    """Registers a new SHG in 'Pending Approval' status with hashed PIN."""
    from services import hash_pin, mask_bank_account

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for duplicate registration ID
    cursor.execute("SELECT id FROM shgs WHERE UPPER(reg_id) = ?;", (reg_id.strip().upper(),))
    if cursor.fetchone():
        conn.close()
        return False, "An SHG with this Govt. Registration ID already exists in the system.", None

    # Generate sequential SHG ID
    cursor.execute("SELECT COUNT(*) + 1 FROM shgs;")
    count = cursor.fetchone()[0]
    shg_id = f"SHG-{count:03d}"

    pin_hash, pin_salt = hash_pin(pin)
    masked_bank = mask_bank_account(bank_ac)
    localities_str = ", ".join(localities_list)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO shgs (
        id, name, portal_type, reg_id, leader_name, phone, localities,
        bank_ac_masked, pin_hash, pin_salt, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Approval', ?);
    """, (
        shg_id, name, portal_type, reg_id.strip().upper(), leader_name,
        phone, localities_str, masked_bank, pin_hash, pin_salt, now_str
    ))

    # Log admin audit
    cursor.execute("""
    INSERT INTO admin_audit (action, target_id, details, actor, timestamp)
    VALUES ('SHG_REGISTERED', ?, ?, 'Self-Registration Portal', ?);
    """, (shg_id, f"SHG '{name}' applied with Reg ID {reg_id}.", now_str))

    conn.commit()
    conn.close()
    return True, f"Registration submitted! Assigned ID {shg_id}. Status: Pending Municipal Approval.", shg_id


def get_all_shgs(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns list of SHGs with optional status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM shgs WHERE status = ? ORDER BY id ASC;", (status_filter,))
    else:
        cursor.execute("SELECT * FROM shgs ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_shg_status(shg_id: str, new_status: str, actor: str, reason: Optional[str] = None) -> bool:
    """Admin approval or rejection of an SHG."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if new_status == "Approved":
        cursor.execute("""
        UPDATE shgs
        SET status = 'Approved', approved_at = ?, approved_by = ?, rejection_reason = NULL
        WHERE id = ?;
        """, (now_str, actor, shg_id))
    elif new_status == "Rejected":
        cursor.execute("""
        UPDATE shgs
        SET status = 'Rejected', rejection_reason = ?, approved_at = NULL, approved_by = ?
        WHERE id = ?;
        """, (reason or "Did not meet verification criteria", actor, shg_id))

    cursor.execute("""
    INSERT INTO admin_audit (action, target_id, details, actor, timestamp)
    VALUES (?, ?, ?, ?, ?);
    """, (f"SHG_{new_status.upper()}", shg_id, f"Status changed to {new_status}. Reason/Note: {reason or 'N/A'}", actor, now_str))

    conn.commit()
    conn.close()
    return True


def get_open_jobs_for_shg(shg_id: str) -> List[Dict[str, Any]]:
    """
    Returns unassigned 'Requested' jobs located in the SHG's operating localities.
    Only approved SHGs can access jobs.
    """
    shg = get_shg_by_id(shg_id)
    if not shg or shg["status"] != "Approved":
        return []

    localities = [loc.strip() for loc in shg["localities"].split(",") if loc.strip()]
    if not localities:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(localities))
    query = f"""
    SELECT * FROM requests
    WHERE status = 'Requested' AND ward IN ({placeholders})
    ORDER BY created_at ASC;
    """
    cursor.execute(query, localities)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_shg_jobs(shg_id: str) -> List[Dict[str, Any]]:
    """Returns all jobs assigned to an SHG."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM requests
    WHERE assigned_shg_id = ?
    ORDER BY updated_at DESC;
    """, (shg_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def accept_job(req_id: str, shg_id: str) -> Tuple[bool, str]:
    """SHG accepts an open request, transitioning to 'Assigned'."""
    shg = get_shg_by_id(shg_id)
    if not shg or shg["status"] != "Approved":
        return False, "Only municipal-approved SHGs can accept pickup jobs."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM requests WHERE id = ?;", (req_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Request not found."

    if row["status"] != "Requested":
        conn.close()
        return False, f"Cannot accept. Current status is {row['status']}."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE requests
    SET status = 'Assigned', assigned_shg_id = ?, assigned_shg_name = ?, updated_at = ?
    WHERE id = ?;
    """, (shg_id, shg["name"], now_str, req_id))

    cursor.execute("""
    INSERT INTO status_history (request_id, from_status, to_status, actor, timestamp, note)
    VALUES (?, 'Requested', 'Assigned', ?, ?, ?);
    """, (req_id, f"SHG: {shg['name']}", now_str, f"Accepted by {shg['name']}."))

    conn.commit()
    conn.close()
    return True, f"Request {req_id} assigned to {shg['name']} successfully."


def mark_collected(
    req_id: str,
    shg_id: str,
    actual_kg: float,
    safety_checked: bool,
    photo_name: Optional[str] = None
) -> Tuple[bool, str]:
    """SHG marks request collected after weighing and verifying safety checklist."""
    if not safety_checked:
        return False, "Safety checklist must be confirmed (PPE worn, battery secured)."

    shg = get_shg_by_id(shg_id)
    if not shg:
        return False, "SHG not recognized."

    from services import calculate_earnings

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE id = ? AND assigned_shg_id = ?;", (req_id, shg_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Request not assigned to this SHG."

    if row["status"] != "Assigned":
        conn.close()
        return False, f"Expected status 'Assigned', but request is currently '{row['status']}'."

    category = row["category"]
    earnings = calculate_earnings(category, actual_kg)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    UPDATE requests
    SET status = 'Collected',
        actual_kg = ?,
        safety_checklist_passed = 1,
        gross_value = ?,
        shg_earnings = ?,
        logistics_fund = ?,
        platform_fee = ?,
        green_credit_fund = ?,
        green_credits_citizen = ?,
        photo_name = COALESCE(?, photo_name),
        updated_at = ?
    WHERE id = ?;
    """, (
        actual_kg,
        earnings["gross_value"],
        earnings["shg_amount"],
        earnings["logistics_amount"],
        earnings["platform_amount"],
        earnings["green_credits_fund"],
        earnings["citizen_credits"],
        photo_name,
        now_str,
        req_id
    ))

    note = f"Collected at doorstep. Actual weight: {actual_kg} kg. Safety PPE verified. Value: ₹{earnings['gross_value']} (SHG Share: ₹{earnings['shg_amount']})."
    cursor.execute("""
    INSERT INTO status_history (request_id, from_status, to_status, actor, timestamp, note)
    VALUES (?, 'Assigned', 'Collected', ?, ?, ?);
    """, (req_id, f"SHG: {shg['name']}", now_str, note))

    conn.commit()
    conn.close()
    return True, f"Marked as Collected! Verified weight: {actual_kg} kg."


def mark_sorted(
    req_id: str,
    shg_id: str,
    sorting_breakdown: Dict[str, float]
) -> Tuple[bool, str]:
    """SHG completes basic segregation into fractions."""
    shg = get_shg_by_id(shg_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE id = ? AND assigned_shg_id = ?;", (req_id, shg_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Request not assigned to this SHG."

    if row["status"] != "Collected":
        conn.close()
        return False, f"Expected status 'Collected', but request is currently '{row['status']}'."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sorting_json = json.dumps(sorting_breakdown)

    cursor.execute("""
    UPDATE requests
    SET status = 'Sorted', sorting_breakdown = ?, updated_at = ?
    WHERE id = ?;
    """, (sorting_json, now_str, req_id))

    note = "Basic segregation into fractions completed. Critical fractions (lithium batteries) stored safely in designated containers."
    cursor.execute("""
    INSERT INTO status_history (request_id, from_status, to_status, actor, timestamp, note)
    VALUES (?, 'Collected', 'Sorted', ?, ?, ?);
    """, (req_id, f"SHG: {shg['name']}", now_str, note))

    conn.commit()
    conn.close()
    return True, "Sorting complete! Ready for authorized recycler dispatch."


def mark_delivered_to_recycler(
    req_id: str,
    shg_id: str,
    recycler_name: str,
    challan_no: str
) -> Tuple[bool, str]:
    """SHG hands over aggregated e-waste to CPCB-authorised recycler with challan."""
    if not recycler_name or not challan_no:
        return False, "Authorized Recycler and Challan Number are mandatory."

    shg = get_shg_by_id(shg_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE id = ? AND assigned_shg_id = ?;", (req_id, shg_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Request not assigned to this SHG."

    if row["status"] != "Sorted":
        conn.close()
        return False, f"Expected status 'Sorted', but request is currently '{row['status']}'."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE requests
    SET status = 'Delivered to Recycler', recycler_name = ?, recycler_challan_no = ?, updated_at = ?
    WHERE id = ?;
    """, (recycler_name, challan_no.strip(), now_str, req_id))

    note = f"Handed over to authorized recycler: {recycler_name}. Challan #{challan_no.strip()}."
    cursor.execute("""
    INSERT INTO status_history (request_id, from_status, to_status, actor, timestamp, note)
    VALUES (?, 'Sorted', 'Delivered to Recycler', ?, ?, ?);
    """, (req_id, f"SHG: {shg['name']}", now_str, note))

    conn.commit()
    conn.close()
    return True, f"Delivered to {recycler_name} under Challan #{challan_no}."


def mark_settled(req_id: str, actor: str) -> Tuple[bool, str]:
    """Municipal admin marks job financial settlement completed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE id = ?;", (req_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Request not found."

    if row["status"] != "Delivered to Recycler":
        conn.close()
        return False, f"Only requests with 'Delivered to Recycler' can be settled (currently '{row['status']}')."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE requests
    SET status = 'Settled', updated_at = ?
    WHERE id = ?;
    """, (now_str, req_id))

    note = f"Recycler certificate and payment reconciled. Payout of ₹{row['shg_earnings']:.2f} finalized for SHG."
    cursor.execute("""
    INSERT INTO status_history (request_id, from_status, to_status, actor, timestamp, note)
    VALUES (?, 'Delivered to Recycler', 'Settled', ?, ?, ?);
    """, (req_id, actor, now_str, note))

    conn.commit()
    conn.close()
    return True, f"Request {req_id} marked as Settled. Payout released."


# ==========================================
# ANALYTICS & DASHBOARD AGGREGATIONS
# ==========================================

def get_kpi_summary() -> Dict[str, Any]:
    """Fetches high-level KPI metrics for landing and admin dashboard."""
    from services import calculate_environmental_impact

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM requests;")
    total_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests WHERE status IN ('Collected', 'Sorted', 'Delivered to Recycler', 'Settled');")
    completed_or_in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'Settled';")
    settled_requests = cursor.fetchone()[0]

    # Total collected tonnage (sum of actual_kg for collected+ requests, or fallback estimated_kg)
    cursor.execute("""
    SELECT COALESCE(SUM(CASE WHEN actual_kg IS NOT NULL THEN actual_kg ELSE estimated_kg END), 0.0)
    FROM requests
    WHERE status IN ('Collected', 'Sorted', 'Delivered to Recycler', 'Settled');
    """)
    total_kg = round(cursor.fetchone()[0], 1)

    # SHGs count
    cursor.execute("SELECT COUNT(*) FROM shgs WHERE status = 'Approved';")
    active_shgs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shgs WHERE status = 'Pending Approval';")
    pending_shgs = cursor.fetchone()[0]

    # Total money paid/earned by SHGs
    cursor.execute("SELECT COALESCE(SUM(shg_earnings), 0.0) FROM requests;")
    total_shg_earnings = round(cursor.fetchone()[0], 2)

    # Total green credits
    cursor.execute("SELECT COALESCE(SUM(green_credits_citizen), 0) FROM requests;")
    total_green_credits = cursor.fetchone()[0]

    conn.close()

    impact = calculate_environmental_impact(total_kg)

    return {
        "total_requests": total_requests,
        "completed_pickups": completed_or_in_progress,
        "settled_requests": settled_requests,
        "total_kg": total_kg,
        "active_shgs": active_shgs,
        "pending_shgs": pending_shgs,
        "total_shg_earnings": total_shg_earnings,
        "total_green_credits": total_green_credits,
        "co2_avoided_kg": impact["co2_avoided_kg"],
        "heavy_metals_prevented_g": impact["heavy_metals_prevented_g"],
        "trees_equivalent": impact["trees_equivalent"]
    }


def get_all_requests_df_data() -> List[Dict[str, Any]]:
    """Returns all requests with masked privacy for admin and table views."""
    from services import mask_phone

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        id, citizen_name, phone, ward, category, estimated_kg, actual_kg,
        pickup_slot, status, assigned_shg_name, gross_value, shg_earnings,
        recycler_name, recycler_challan_no, created_at, updated_at
    FROM requests
    ORDER BY seq_num DESC;
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["phone_masked"] = mask_phone(d["phone"])
        result.append(d)
    return result


def get_tonnage_by_category() -> List[Dict[str, Any]]:
    """Returns tonnage and request count grouped by e-waste category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        category,
        COUNT(*) as request_count,
        ROUND(SUM(COALESCE(actual_kg, estimated_kg)), 2) as total_kg,
        ROUND(SUM(gross_value), 2) as total_value
    FROM requests
    GROUP BY category
    ORDER BY total_kg DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tonnage_by_ward() -> List[Dict[str, Any]]:
    """Returns ward-wise collection breakdown for Meerut."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        ward,
        COUNT(*) as request_count,
        ROUND(SUM(COALESCE(actual_kg, estimated_kg)), 2) as total_kg
    FROM requests
    GROUP BY ward
    ORDER BY total_kg DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tonnage_timeline() -> List[Dict[str, Any]]:
    """Returns monthly / weekly tonnage progression."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        SUBSTR(created_at, 1, 10) as day_date,
        COUNT(*) as count,
        ROUND(SUM(COALESCE(actual_kg, estimated_kg)), 2) as daily_kg
    FROM requests
    GROUP BY day_date
    ORDER BY day_date ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_status_funnel_data() -> List[Dict[str, Any]]:
    """Returns counts for each stage in the status funnel."""
    from services import STATUS_ORDER
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM requests
    GROUP BY status;
    """)
    rows = cursor.fetchall()
    conn.close()

    count_map = {r["status"]: r["count"] for r in rows}
    return [{"status": s, "count": count_map.get(s, 0)} for s in STATUS_ORDER]


def get_shg_leaderboard() -> List[Dict[str, Any]]:
    """Returns leaderboard of SHGs ranked by total kg collected and earnings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        s.id,
        s.name,
        s.portal_type,
        s.reg_id,
        s.leader_name,
        COUNT(r.id) as jobs_assigned,
        COUNT(CASE WHEN r.status IN ('Collected', 'Sorted', 'Delivered to Recycler', 'Settled') THEN 1 END) as jobs_completed,
        ROUND(SUM(COALESCE(r.actual_kg, 0.0)), 2) as total_kg_collected,
        ROUND(SUM(COALESCE(r.shg_earnings, 0.0)), 2) as total_earnings
    FROM shgs s
    LEFT JOIN requests r ON s.id = r.assigned_shg_id
    WHERE s.status = 'Approved'
    GROUP BY s.id
    ORDER BY total_kg_collected DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_exception_alerts() -> Dict[str, Any]:
    """
    Returns critical operational exceptions:
    1. Requests unassigned for > 48 hours.
    2. Approved SHGs with 0 activity in the last 30 days.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Unassigned > 48 hours: status = 'Requested' and created_at < now - 48 hours
    cutoff = (datetime.now() - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    SELECT id, citizen_name, ward, category, estimated_kg, created_at
    FROM requests
    WHERE status = 'Requested' AND created_at < ?
    ORDER BY created_at ASC;
    """, (cutoff,))
    stale_requests = [dict(r) for r in cursor.fetchall()]

    # SHGs with 0 completed pickups
    cursor.execute("""
    SELECT s.id, s.name, s.leader_name, s.phone, s.created_at
    FROM shgs s
    LEFT JOIN requests r ON s.id = r.assigned_shg_id AND r.status IN ('Collected', 'Sorted', 'Delivered to Recycler', 'Settled')
    WHERE s.status = 'Approved'
    GROUP BY s.id
    HAVING COUNT(r.id) = 0;
    """)
    inactive_shgs = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "stale_requests": stale_requests,
        "inactive_shgs": inactive_shgs
    }


def get_citizen_leaderboard() -> List[Dict[str, Any]]:
    """Returns top citizen green credit champions (first name + locality only for privacy)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        citizen_name,
        ward,
        SUM(green_credits_citizen) as total_credits,
        ROUND(SUM(COALESCE(actual_kg, estimated_kg)), 1) as total_kg
    FROM requests
    GROUP BY citizen_name, ward
    ORDER BY total_credits DESC
    LIMIT 10;
    """)
    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
    for r in rows:
        full_name = r["citizen_name"].strip()
        first_name = full_name.split()[0] if full_name else "Citizen"
        leaderboard.append({
            "name": f"{first_name} ({r['ward']})",
            "credits": r["total_credits"],
            "kg": r["total_kg"]
        })
    return leaderboard


def get_full_audit_history() -> List[Dict[str, Any]]:
    """Returns master audit trail with request metadata for compliance exports."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        h.id as audit_id,
        h.request_id,
        r.category,
        r.ward,
        h.from_status,
        h.to_status,
        h.actor,
        h.timestamp,
        h.note,
        r.actual_kg,
        r.recycler_name,
        r.recycler_challan_no
    FROM status_history h
    JOIN requests r ON h.request_id = r.id
    ORDER BY h.id DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
