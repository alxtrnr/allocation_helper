# Data Integrity Fix: Staff Duration Auto-Correction

## Problem

The application was experiencing solver infeasibility issues due to inconsistent staff data where the `duration` field did not match the actual working hours (`end_time - start_time`). This inconsistency caused the solver's break constraint to be applied incorrectly.

### Root Cause

The `duration` field was being set independently of `start_time` and `end_time`, allowing them to diverge. For example:
- Staff member "Benny" had `start_time=1`, `end_time=2` (1 hour of work)
- But `duration=12` (indicating a 12-hour shift)
- This made the break constraint impossible to satisfy for a 1-hour shift

The issue occurred because:
1. The UI layer directly modified time fields without updating `duration`
2. The service layer accepted `duration` as an independent parameter without validation
3. There was no automatic synchronization between these related fields

## Solution

### 1. Service Layer Validation and Auto-Correction

**File:** `services/staff_service.py`

Added comprehensive validation and automatic correction in both `add_staff_entry` and `update_staff_entry`:

```python
# Validate time range
if start_time < 0 or start_time > 12:
    return {'success': False, 'message': 'Start time must be between 0 and 12.'}
if end_time < 0 or end_time > 12:
    return {'success': False, 'message': 'End time must be between 0 and 12.'}
if start_time >= end_time:
    return {'success': False, 'message': 'End time must be greater than start time.'}

# Auto-correct duration to match actual working hours
actual_hours = end_time - start_time
if duration != actual_hours:
    duration = actual_hours  # Auto-correct
```

### 2. UI Layer Synchronization

**File:** `database_utils/database_operations.py`

Modified the staff data editor to automatically update `duration` when times are changed:

```python
# When start_time is updated
db_entry.start_time = new_start_time
db_entry.duration = db_entry.end_time - db_entry.start_time

# When end_time is updated
db_entry.end_time = new_end_time
db_entry.duration = db_entry.end_time - db_entry.start_time
```

### 3. Database Migration Script

**File:** `fix_existing_data.py`

Created a one-time migration script to fix any existing inconsistent records:

```python
for staff in staff_list:
    actual_hours = staff.end_time - staff.start_time
    if staff.duration != actual_hours:
        staff.duration = actual_hours
        fixed_count += 1
```

### 4. Comprehensive Test Suite

**File:** `services/test_staff_validation.py`

Added 6 comprehensive tests covering:
- Auto-correction during staff creation
- Auto-correction during staff updates
- Time range validation
- Implicit duration correction (when not explicitly provided)
- Various shift lengths

## Benefits

1. **No Manual Intervention Required**: The application automatically maintains data consistency
2. **Prevents Future Issues**: All entry points now validate and auto-correct data
3. **Backward Compatible**: Automatically fixes legacy data without user action
4. **Tested**: Comprehensive test suite ensures reliability
5. **User-Friendly**: Users don't need to think about duration - it's calculated automatically

## Impact on Solver

With this fix:
- The `duration` field always matches actual working hours
- Break constraints are applied correctly based on actual shift length
- No more infeasibility due to impossible break requirements
- Solver produces correct, gap-free allocations

## Verification

Run the validation test suite:
```bash
python3 -m pytest services/test_staff_validation.py -v
```

Check existing database data:
```bash
python3 fix_existing_data.py
```

## Technical Details

### Why Duration Matters

The solver uses `duration` to determine which break constraint to apply:
- `duration >= 12`: Requires 2 consecutive unassigned hours in slots 5-11
- `duration < 12`: No break constraint

If `duration` doesn't match actual hours:
- A 1-hour shift with `duration=12` would require an impossible 2-hour break
- This causes the solver to report "infeasible"

### Data Consistency Rule

**Invariant:** `duration` MUST ALWAYS equal `end_time - start_time`

This invariant is now enforced at:
1. ✅ Service layer (add/update operations)
2. ✅ UI layer (direct database modifications)
3. ✅ Migration script (fixes existing data)

## Migration History

- **2025-10-31**: Initial fix implemented across all layers
- Fixed existing database records for: Benny (duration: 12 → 1)
- All 6 validation tests passing
- Solver now produces feasible, gap-free allocations

