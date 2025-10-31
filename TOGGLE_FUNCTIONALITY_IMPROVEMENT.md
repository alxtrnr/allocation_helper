# Toggle Functionality Improvement: Cherry Pick & Exclude Staff

## Issue

Users reported that when selecting staff to exclude from a patient's observations, or when cherry-picking patients for a staff member, there was **no clear way to revert the decision**. The UI didn't make it obvious that:

1. The feature uses a **toggle** mechanism
2. You can **remove** selections by selecting them again
3. What's currently selected/excluded

## Solution Implemented

### 1. Clearer Column Labels

**Before:**
- Staff table: "Selector" → "Cherry Pick"
- Patient table: "Selector" → "Omit Staff"

**After:**
- Staff table: **"Add/Remove"** → **"Cherry Pick List"**
- Patient table: **"Add/Remove"** → **"Excluded Staff"**

The new labels make it clear that:
- The first column is for **adding AND removing**
- The second column **shows the current list**

### 2. Enhanced Tooltips

**Staff Table - Add/Remove Column:**
```
Select a patient to ADD to or REMOVE from the Cherry Pick list.
If already in the list, selecting will remove them.
Check the Cherry Pick column to see current selections.
```

**Staff Table - Cherry Pick List Column:**
```
Current patients this staff can ONLY observe.
Use Add/Remove column to toggle.
Empty = can observe any patient.
```

**Patient Table - Add/Remove Column:**
```
Select a staff member to ADD to or REMOVE from the exclusion list.
If already excluded, selecting will UN-EXCLUDE them.
Check the Omit Staff column to see current exclusions.
```

**Patient Table - Excluded Staff Column:**
```
Staff listed here will NOT be allocated to this patient.
Use Add/Remove column to toggle.
Empty = any staff can be assigned.
```

### 3. Informational Banners

Added prominent info boxes above each data editor:

**Staff Table:**
```
💡 Cherry Pick: Use the 'Add/Remove' dropdown to select patients.
If a patient is already in the 'Cherry Pick List', selecting them
again will remove them. The list shows which patients this staff
member can exclusively observe.
```

**Patient Table:**
```
💡 Exclude Staff: Use the 'Add/Remove' dropdown to select staff
members to exclude. If a staff member is already in the 'Excluded
Staff' list, selecting them again will un-exclude them. The list
shows which staff will NOT be assigned to this patient.
```

### 4. Column Width Adjustments

Changed the display columns from `width="small"` to `width="medium"` so users can see longer lists of names without truncation.

## How It Works

### Toggle Mechanism

The existing toggle code (no changes needed):

```python
# For staff cherry-picking patients
if df_entry:
    if df_entry not in db_entry.special_list:
        db_entry.special_list.append(df_entry)  # ADD
    elif df_entry in db_entry.special_list:
        db_entry.special_list.pop(
            db_entry.special_list.index(df_entry))  # REMOVE

# For patients excluding staff
if df_entry:
    if df_entry not in db_entry.omit_staff:
        db_entry.omit_staff.append(df_entry)  # ADD
    elif df_entry in db_entry.omit_staff:
        db_entry.omit_staff.pop(
            db_entry.omit_staff.index(df_entry))  # REMOVE
```

### User Workflow

**To Add a Selection:**
1. Use the "Add/Remove" dropdown
2. Select the name you want to add
3. The name appears in the adjacent list column
4. Changes save automatically

**To Remove a Selection:**
1. Use the "Add/Remove" dropdown
2. Select the **same name** again
3. The name disappears from the list column
4. Changes save automatically

**To See Current Selections:**
- Look at the "Cherry Pick List" or "Excluded Staff" column
- Empty = no restrictions

## User Experience Impact

### Before
- ❌ Users didn't know selections could be removed
- ❌ Unclear how the toggle mechanism worked
- ❌ No indication of what was currently selected
- ❌ Column labels were ambiguous

### After
- ✅ Clear instructions that selections toggle on/off
- ✅ Explicit "Add/Remove" label indicates two-way action
- ✅ Display column clearly shows current state
- ✅ Info banner explains the feature before use
- ✅ Tooltips provide context-sensitive help

## Examples

### Staff Cherry-Picking Example

**Scenario:** Alexander should only observe Donna Mcarthur

1. Go to Staff tab
2. Find Alexander's row
3. See the info banner explaining toggle functionality
4. In "Add/Remove" column, select "Donna Mcarthur"
5. "Donna Mcarthur" appears in "Cherry Pick List" column
6. Alexander can now **only** be assigned to Donna

**To Revert:**
1. In "Add/Remove" column, select "Donna Mcarthur" **again**
2. "Donna Mcarthur" disappears from "Cherry Pick List"
3. Alexander can now observe **any** patient

### Patient Exclusion Example

**Scenario:** Barry Brown should not be observed by Benny

1. Go to Patients tab
2. Find Barry Brown's row
3. See the info banner explaining toggle functionality
4. In "Add/Remove" column, select "Benny"
5. "Benny" appears in "Excluded Staff" column
6. Benny will **not** be assigned to Barry

**To Revert:**
1. In "Add/Remove" column, select "Benny" **again**
2. "Benny" disappears from "Excluded Staff"
3. Benny **can** now be assigned to Barry

## Technical Details

### Files Modified

**`database_utils/database_operations.py`**

Changes made:
1. Renamed "Selector" to "Add/Remove" (lines 249, 496)
2. Updated column labels for clarity
3. Enhanced tooltips with toggle instructions
4. Added info banners explaining functionality
5. Increased column width for better visibility

No changes to backend logic - only UI improvements.

## Testing

### Manual Testing

**Test 1: Add and Remove Cherry Pick**
1. Go to Staff tab
2. Select a patient in "Add/Remove"
3. Verify patient appears in "Cherry Pick List"
4. Select same patient again
5. Verify patient disappears from list

**Test 2: Add and Remove Excluded Staff**
1. Go to Patients tab
2. Select a staff member in "Add/Remove"
3. Verify staff appears in "Excluded Staff"
4. Select same staff again
5. Verify staff disappears from list

**Test 3: Info Banner Visibility**
1. Go to Staff tab
2. Verify blue info banner appears above table
3. Go to Patients tab
4. Verify blue info banner appears above table

## Benefits

1. **Self-Explanatory:** Users understand toggle behavior without training
2. **Visible State:** Current selections are always visible
3. **Reversible:** Clear path to undo selections
4. **Consistent:** Same pattern for both staff and patient tables
5. **Professional:** Helpful UI that guides users

## Future Enhancements

Potential improvements:
1. Visual indicator (e.g., checkmark icon) when a name is in the list
2. "Clear All" button to remove all selections at once
3. Multi-select capability to add/remove multiple names at once
4. Confirmation dialog when removing last selection
5. Search/filter in dropdown for large staff/patient lists

## Summary

✅ **Problem:** Users couldn't figure out how to revert cherry-pick/exclusion decisions
✅ **Solution:** Enhanced UI with clear labels, tooltips, and info banners
✅ **Result:** Self-explanatory toggle functionality that's easy to use and understand

The feature now clearly communicates:
- What it does (restrict assignments)
- How to use it (select to add/remove)
- How to revert it (select again to toggle off)
- Current state (visible in list column)

