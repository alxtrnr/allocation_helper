# Infeasibility Analysis Report

## Problem Statement

The solver reports "Status: Infeasible" even though basic coverage appears adequate.

## Root Cause

**Break Window Capacity Shortage**

The problem becomes infeasible due to the **12-hour break constraint** creating insufficient capacity during slots 5-11.

### The Mathematics

**Constraint:** Staff working ≥12 hours must have 2 consecutive hours unassigned during slots 5-11 (the break window).

**Current Situation:**
- **8 staff** working 12-hour shifts (Alexander, Justine, Damian, Michael, Oscar, Otis, Malachi, Elijah)
- **Break requirement:** Each can work **maximum 5 of 7 slots** (5-11)
- **Available capacity:** 8 staff × 5 slots = **40 staff-slots**

**Observation Needs:**
- **7 slots** (5-11) × **7 staff needed per slot** = **49 staff-slots required**

**Result:** 40 < 49 → **INFEASIBLE**

## Why This Happens

Even though you have 8-9 staff available at any given hour, the break constraint reduces their effective availability:

```
Without breaks: 8 staff × 7 slots = 56 staff-slots ✓ (enough)
With breaks:    8 staff × 5 slots = 40 staff-slots ✗ (insufficient)
```

The 2-hour break requirement removes 16 staff-slots from the system during the critical break window.

## Verification

Run this to verify:
```bash
python3 << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import StaffTable, PatientTable

engine = create_engine('sqlite:///ward_db_alxtrnr.db')
Session = sessionmaker(bind=engine)
session = Session()

staff_12h = session.query(StaffTable).filter(
    StaffTable.assigned == True,
    StaffTable.duration >= 12
).count()

patient_need = sum(int(p.observation_level or 0) 
                   for p in session.query(PatientTable).all())

capacity = staff_12h * 5  # max 5 of 7 slots
required = patient_need * 7  # 7 slots in break window

print(f"12h staff: {staff_12h}")
print(f"Need per slot: {patient_need}")
print(f"Capacity: {capacity} staff-slots")
print(f"Required: {required} staff-slots")
print(f"Feasible: {capacity >= required}")

session.close()
EOF
```

## Solutions

### Solution 1: Add Staff (Recommended)

Add **2 additional staff members** who work during the break window.

**Option A: Add full-time staff**
```python
# Add 2 more staff working 12h shifts
# This gives: 10 staff × 5 slots = 50 staff-slots ✓
```

**Option B: Add part-time staff for break coverage**
```python
# Add staff who work ONLY during break window (slots 5-11)
# Shorter shifts = different break requirements
# Example: 5-11 is 6 hours → only needs 1h break
```

### Solution 2: Stagger Shifts

Instead of all staff working 0-12, stagger their shifts:

```
Current:  8 staff × (0-12, 12h) + 1 staff × (1-2, 1h)
Modified: 4 staff × (0-11, 11h)  → need 1h break
          4 staff × (1-12, 11h)  → need 1h break
          1 staff × (0-12, 12h)  → need 2h break
```

11-hour shifts only require a **1-hour break** (more flexible constraint), increasing effective capacity.

### Solution 3: Reduce Observation Needs

Reduce observation levels for some patients during afternoon hours (slots 5-11):

```
Current: 7 staff needed per slot
Target:  5-6 staff needed per slot
Capacity with breaks: 8 × 5 / 7 ≈ 5.7 staff per slot
```

### Solution 4: Modify Break Constraint (Not Recommended)

Change the break requirement:
- From: "2 consecutive hours in slots 5-11" 
- To: "2 hours total (not necessarily consecutive)"

⚠️ This may violate labor regulations and staff welfare policies.

## Implementation

### Quick Fix: Add 2 Staff Members

In the Streamlit UI:
1. Go to "Staff" tab
2. Add 2 new staff members
3. Set them as "Assigned"
4. Set working hours: 0-12 (or 5-11 for targeted coverage)
5. Re-run allocations

### Alternative: Stagger Shifts

Modify existing staff:
1. Select 4 staff members
2. Change end time from 12 to 11 (11-hour shift)
3. This reduces their break requirement from 2h to 1h
4. Re-run allocations

## Why The Table Shows Assignments

The table you see in the UI might be showing a **partial or infeasible solution** that the solver explored before determining infeasibility. The CBC solver may output intermediate results even when the final status is "Infeasible."

Alternatively, if using a cached previous solution, the UI might display old results while the current solver run fails.

## Recommended Action

**Immediate:** Add 2 more staff members working 12-hour shifts (or 4+ staff working 6-hour shifts during the break window).

**Long-term:** Consider a staff scheduling system that:
- Staggers shift start/end times
- Mixes 11h and 12h shifts for better flexibility
- Maintains a buffer of 2-3 extra staff for break coverage

## Verification After Fix

After implementing a solution:

1. Check capacity:
```bash
python3 -c "from services.staff_service import check_allocation_feasibility; from sqlalchemy import create_engine; from sqlalchemy.orm import sessionmaker; engine = create_engine('sqlite:///ward_db_alxtrnr.db'); Session = sessionmaker(bind=engine); print(check_allocation_feasibility(Session()()))"
```

2. Run allocations in Streamlit

3. Verify status is "Optimal" or "Feasible" (not "Infeasible")

## Summary

- ✅ Basic coverage is adequate (8 available vs 7 needed)
- ✅ Data integrity is correct (duration matches hours)
- ✅ Special lists are configured correctly
- ❌ **Break window capacity is insufficient** (40 vs 49 staff-slots needed)

The application is working correctly - it's identifying a real constraint violation that makes the schedule infeasible under current staffing levels and break requirements.

