# Solver Constraints - Quick Reference

## 11 Constraint Categories (All Hard Constraints)

### 📋 Patient Requirements
1. **Observation Levels** (0, 1:1, 2:1, 3:1, 4:1)
   - Level 0: No staff needed
   - Level N: Exactly N staff required at all times

2. **Gender Requirements**
   - Patient can require specific gender staff (M or F)
   - Excludes incompatible staff automatically

### 👤 Staff Availability
3. **Assigned Status**
   - Only staff marked "Assign" ✅ in UI are included
   
4. **Working Hours**
   - Staff only work between Start and End times
   - Configure in Staff page (e.g., "08:00" to "19:00")

5. **Omit Times**
   - Exclude staff at specific hours (breaks, meetings)
   - Format: "13:00 14:00" for lunch at 1pm-2pm

### 🚫 Exclusions
6. **Patient Excludes Staff**
   - Patient can exclude specific staff by name
   - Configure in Patient page "Omit Staff" column

7. **Staff Special List** (Cherry-Picking)
   - Staff with special_list ONLY observe those patients
   - Configure in Staff page "Cherry Pick" column

### ⚖️ Workload Rules
8. **One Patient Per Staff**
   - Each staff observes max 1 patient at any time
   - (Multiple staff can observe same patient for 2:1, 3:1, 4:1)

9. **Consecutive Hours Limit**
   - Max 2 consecutive hours per staff-patient pair
   - Staff CAN switch between patients every 2 hours

### 💤 Break Requirements
10. **Short Shifts** (< 12 hours)
    - At least 1 break hour per 2-hour window
    - Applies after first 3 hours of shift

11. **Long Shifts** (≥ 12 hours)
    - At least 2 break hours in slots 5-11
    - For 12-hour shift: 2+ hours off between 13:00-19:00

---

## Time Slots (12 per shift)

| Slot | Day Shift | Night Shift |
|------|-----------|-------------|
| 0    | 08:00-09:00 | 20:00-21:00 |
| 1    | 09:00-10:00 | 21:00-22:00 |
| 2    | 10:00-11:00 | 22:00-23:00 |
| 3    | 11:00-12:00 | 23:00-00:00 |
| 4    | 12:00-13:00 | 00:00-01:00 |
| 5    | 13:00-14:00 | 01:00-02:00 |
| 6    | 14:00-15:00 | 02:00-03:00 |
| 7    | 15:00-16:00 | 03:00-04:00 |
| 8    | 16:00-17:00 | 04:00-05:00 |
| 9    | 17:00-18:00 | 05:00-06:00 |
| 10   | 18:00-19:00 | 06:00-07:00 |
| 11   | 19:00-20:00 | 07:00-08:00 |

---

## Common Infeasibility Causes

❌ **Not enough staff hours** → Add more staff or reduce observation levels
❌ **Invalid time ranges (0-0)** → Set Start/End times in Staff page  
❌ **Staff not assigned** → Check "Assign" checkbox in Staff page
❌ **Gender conflicts** → Ensure staff of required gender are available
❌ **Special list too restrictive** → Add more staff or remove restrictions
❌ **Break constraints impossible** → Add staff to cover break periods

---

## Configuration Checklist

### Before Running Allocations:
- [ ] Staff marked as "Assign" ✅
- [ ] Start and End times set (e.g., "08:00", "19:00")
- [ ] Observation levels set on patients (0-4)
- [ ] Gender requirements set if needed
- [ ] Special lists / exclusions configured if needed
- [ ] Run feasibility check (happens automatically)

### If Infeasible:
1. Run `python3 diagnose_and_fix_db.py`
2. Check feasibility warnings for specific hours
3. Add more staff or adjust constraints
4. Verify time ranges are valid

---

---

## ⭐ New: Workload Optimization

The solver now **minimizes workload imbalance** to ensure fair distribution:

**Example:** With 3 staff and 6 hours work:
- ❌ Before: 6-0-0 (very imbalanced)
- ✅ Now: 2-2-2 (perfectly balanced)

See `WORKLOAD_OPTIMIZATION.md` for full details.

---

## Tools & Documentation

- `SOLVER_CONSTRAINTS.md` - Full detailed constraints documentation
- `WORKLOAD_OPTIMIZATION.md` - Workload balancing optimization explained
- `diagnose_and_fix_db.py` - Diagnostic tool for configuration issues
- `DATABASE_FIX_REPORT.md` - Guide to fixing database problems
- `SOLVER_FIXES.md` - Recent bug fixes and improvements

