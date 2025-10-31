# Database Configuration Fix Report

## Issue Summary

The solver was reporting "available 0" staff for all hours, making allocations infeasible even though staff existed in the database.

## Root Cause

**Staff had invalid time ranges configured in the database:**

- 9 out of 10 staff members had `start_time = 0` and `end_time = 0`
- This means they were configured to work from hour 0 to hour 0 (i.e., 0 hours of availability)
- The feasibility check correctly identified that no staff were available for any time slots

### Database State Before Fix

```
ID | Name       | Assigned | Start Time | End Time
---|------------|----------|------------|----------
 1 | Alexander  | ✅ True  |     0      |    0     ❌
 2 | Justine    | ✅ True  |     0      |    0     ❌
 3 | Damian     | ✅ True  |     0      |    0     ❌
... (6 more with same issue)
10 | Benny      | ✅ True  |     1      |    2     (only 1 hour available)
```

### How This Happens

In the Streamlit UI staff editor:
1. The `Start` and `End` columns accept time strings like "08:00", "19:00"
2. These are converted to integer indices (0-11) representing the 12 hourly time slots
3. If the `Start` and `End` fields are left empty or set to invalid values, the conversion defaults to 0

The columns `start_time` and `end_time` store these integer indices:
- Day shift: "08:00" → `start_time=0`, "19:00" → `end_time=12` (covers slots 0-11)
- Night shift: "20:00" → `start_time=0`, "07:00" → `end_time=12` (covers slots 0-11)

## Fix Applied

Updated the 9 staff members with invalid time ranges to default day shift configuration:

```sql
UPDATE staff_table 
SET start_time = 0, 
    end_time = 12, 
    start = '08:00', 
    end = '19:00'
WHERE start_time = 0 AND end_time = 0
```

### Database State After Fix

```
ID | Name       | Assigned | Start Time | End Time | Coverage
---|------------|----------|------------|----------|----------
 1 | Alexander  | ✅ True  |     0      |   12     | 0-11 ✅
 2 | Justine    | ✅ True  |     0      |   12     | 0-11 ✅
 3 | Damian     | ✅ True  |     0      |   12     | 0-11 ✅
... (all now have full day shift coverage)
```

## Verification

After the fix, the feasibility check now correctly reports:

```
✅ Success: True
Message: Coverage is feasible for all hours.
```

With 9 staff available for all 12 hours and only 1 patient requiring 1:1 observation, the allocations are now feasible.

## How to Properly Configure Staff in the UI

### Using the Staff Page in Streamlit

1. Navigate to the **Staff** page (page 2)
2. Find the data editor table showing all staff
3. For each staff member who should work:
   - ✅ Check the **"Assign"** checkbox (includes them in allocations)
   - Set **"Start"** time:
     - Day shift: `08:00` or `08:00` (or any valid HH:00 format)
     - Night shift: `20:00`
   - Set **"End"** time:
     - Day shift: `19:00` (gives 0-11 coverage in day hours)
     - Night shift: `07:00` (gives 0-11 coverage in night hours)
   - Optionally set **"Omit"** times (e.g., `13:00 14:00` for lunch break)

### Time Slot Mapping

The solver uses 12 hourly time slots (0-11):

**Day Shift:**
- Slot 0 = 08:00-09:00
- Slot 1 = 09:00-10:00
- ...
- Slot 11 = 19:00-20:00

**Night Shift:**
- Slot 0 = 20:00-21:00
- Slot 1 = 21:00-22:00
- ...
- Slot 11 = 07:00-08:00

### Common Configurations

| Shift Type | Start | End  | Duration | Slots Covered |
|------------|-------|------|----------|---------------|
| Long Day   | 08:00 | 19:00| 12 hours | 0-11 (all)    |
| Long Night | 20:00 | 07:00| 12 hours | 0-11 (all)    |
| Short Day  | 08:00 | 13:00| 6 hours  | 0-5           |
| Late Shift | 13:00 | 19:00| 6 hours  | 5-11          |

## Diagnostic Tool

A diagnostic script `diagnose_and_fix_db.py` has been created to help identify and fix these issues:

```bash
python3 diagnose_and_fix_db.py
```

This will:
- Show how many staff are assigned vs. unassigned
- Identify staff with invalid time ranges
- Show patient observation requirements
- Calculate feasibility for each hour
- Offer to fix common issues automatically

## Prevention

To prevent this issue in the future:

1. **Always set Start and End times** when adding new staff in the UI
2. Use the diagnostic script periodically to check configuration
3. Consider adding UI validation to prevent empty/invalid time ranges
4. The feasibility check will warn you before trying to solve if configuration is invalid

## Related Files

- `diagnose_and_fix_db.py` - Diagnostic and repair tool
- `services/staff_service.py` - Contains `check_allocation_feasibility()`
- `database_utils/database_operations.py` - Staff data editor UI
- `utils/time_utils.py` - Time conversion utilities

