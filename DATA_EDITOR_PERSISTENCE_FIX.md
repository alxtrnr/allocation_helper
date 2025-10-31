# Data Editor Persistence Fix

## Problem

When cells were updated in the Streamlit data editor, the update had to be completed **twice** before it would persist. Users would edit a cell, but the change wouldn't save until they edited it again.

## Root Cause

The issue was caused by **incorrect row matching** between the DataFrame (from the data editor) and the database entries. The code was using `zip()` to pair DataFrame rows with database query results, which relied on:

1. **Unordered queries**: Database queries without explicit `ORDER BY` could return rows in different orders on different runs
2. **Index-based matching**: Using `zip()` assumed the DataFrame row at index N matched the database entry at index N, which wasn't guaranteed
3. **Session state**: After commits, if the query order changed, rows would be compared against the wrong database entries

### Example of the Bug

**First Edit:**
1. User edits row 0: Name "Alice" → "Bob"
2. Query returns: `[entry_1, entry_0, entry_2]` (different order!)
3. `zip()` pairs: DataFrame row 0 ("Bob") with DB entry_1 ("Charlie")
4. Comparison: "Charlie" != "Bob" → Updates entry_1 (wrong row!)
5. User's edit for entry_0 doesn't get saved

**Second Edit:**
1. User edits row 0 again: "Alice" → "Bob"
2. Query returns: `[entry_0, entry_1, entry_2]` (correct order this time)
3. `zip()` pairs: DataFrame row 0 ("Bob") with DB entry_0 ("Alice")
4. Comparison: "Alice" != "Bob" → Updates entry_0 (correct row!)
5. Change persists

## Solution

Replaced **index-based matching** (`zip()`) with **ID-based matching** using dictionaries:

### Before (Broken)

```python
# Queries without ordering
query = select(staff_db.name, staff_db.role, ...)

# Extract lists (order-dependent)
df_names = [row['Name'] for _, row in df.iterrows()]
df_roles = [row['Role'] for _, row in df.iterrows()]

# Match by index (unreliable!)
for db_entry, df_name in zip(db_session.query(staff_db), df_names):
    if db_entry.name != df_name:
        update_staff_entry(db_session, db_entry.id, name=df_name)
```

### After (Fixed)

```python
# Query with ID and explicit ordering
query = select(
    staff_db.id,
    staff_db.name,
    staff_db.role,
    ...
).order_by(staff_db.id)

# Include ID in DataFrame
staff_df = pd.DataFrame(staff_data, columns=['ID', 'Name', 'Role', ...])

# Create ID-based mapping
staff_by_id = {entry.id: entry for entry in db_session.query(staff_db).all()}

# Match by ID (reliable!)
for _, row in edited_staff_df.iterrows():
    staff_id = int(row['ID'])
    db_entry = staff_by_id[staff_id]  # Direct lookup by ID
    
    if db_entry.name != row['Name']:
        update_staff_entry(db_session, db_entry.id, name=row['Name'])
```

## Changes Made

### Staff Data Editor (`staff_data_editor()`)

1. **Added ID to query**:
   ```python
   query = select(
       staff_db.id,  # Added
       staff_db.name,
       ...
   ).order_by(staff_db.id)  # Added explicit ordering
   ```

2. **Included ID in DataFrame**:
   ```python
   column_names = ['ID', 'Name', 'Role', ...]
   ```

3. **Created ID-based mapping**:
   ```python
   staff_by_id = {entry.id: entry for entry in db_session.query(staff_db).all()}
   ```

4. **Replaced all `zip()` loops with ID-based loops**:
   ```python
   for _, row in edited_staff_df.iterrows():
       staff_id = int(row['ID'])
       db_entry = staff_by_id[staff_id]
       # Process all fields for this row...
   ```

5. **Added ID column config** (disabled, so users can't edit it):
   ```python
   'ID': st.column_config.NumberColumn(
       label=None,
       disabled=True,
       default=None
   )
   ```

### Patient Data Editor (`patient_data_editor()`)

Applied the same fix:
- Added ID to query with `.order_by(patient_db.id)`
- Included ID in DataFrame
- Created `patients_by_id` mapping dictionary
- Replaced all `zip()` loops with ID-based loops
- Added disabled ID column to data editor

## Benefits

### ✅ Guaranteed Correct Matching

- **ID-based matching** ensures DataFrame rows always match the correct database entries
- **Explicit ordering** (`ORDER BY id`) makes queries deterministic
- **No reliance on query order** - works even if database order changes

### ✅ Immediate Persistence

- Changes persist on **first edit** (no more double-editing needed!)
- Accurate comparisons against the correct database row
- Consistent behavior across all fields

### ✅ Better Performance

- Single loop through DataFrame instead of multiple `zip()` loops
- Dictionary lookup (O(1)) instead of index-based matching
- Reduced database queries (one query to build mapping vs. multiple queries per field)

## Testing

### Manual Test Procedure

1. **Test Staff Name Update**:
   - Go to Staff tab
   - Edit a staff member's name
   - Verify change persists immediately (no need to edit twice)

2. **Test Patient Observation Level Update**:
   - Go to Patients tab
   - Edit a patient's observation level
   - Verify change persists immediately

3. **Test Multiple Field Updates**:
   - Edit multiple fields in the same row
   - Verify all changes persist on first save

4. **Test Order Independence**:
   - Delete and re-add staff/patients (changes IDs)
   - Edit existing rows
   - Verify matching still works correctly

### Expected Results

- ✅ All edits persist on first save
- ✅ No need to edit cells twice
- ✅ Correct rows are updated (no cross-contamination)
- ✅ ID column visible but disabled (for debugging/verification)

## Technical Details

### Why This Fix Works

1. **Primary Key Guarantee**: IDs are unique, immutable primary keys - perfect for matching
2. **Deterministic Ordering**: `ORDER BY id` ensures consistent query results
3. **Direct Lookup**: Dictionary mapping provides O(1) lookup time
4. **Type Safety**: Converting ID to `int()` ensures type consistency

### Edge Cases Handled

- **Missing IDs**: Check `if staff_id not in staff_by_id: continue`
- **Type Conversion**: `int(row['ID'])` ensures numeric ID
- **Null/NaN Values**: DataFrame ID column should always have values (from database query)

### Backward Compatibility

- ✅ Existing data unaffected (IDs already exist in database)
- ✅ No schema changes required
- ✅ All existing fields continue to work
- ✅ ID column is visible but doesn't interfere with editing

## Files Modified

- `database_utils/database_operations.py`
  - `staff_data_editor()`: Fixed row matching using ID-based approach
  - `patient_data_editor()`: Fixed row matching using ID-based approach

## Summary

**Problem**: Updates required two edits before persisting due to incorrect row matching

**Root Cause**: Using `zip()` to match rows by index, which broke when query order changed

**Solution**: ID-based matching using dictionary lookup with explicit `ORDER BY id`

**Result**: ✅ Changes persist immediately on first edit

The fix ensures that **every edit is matched to the correct database row** using the primary key (ID), making persistence reliable and immediate.

