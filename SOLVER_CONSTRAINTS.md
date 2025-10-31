# Staff Allocation Solver: Complete Constraints Documentation

## Overview

The solver uses **Mixed Integer Linear Programming (MILP)** with the CBC solver via PuLP to assign staff to patient observations across 12 hourly time slots per shift.

### Decision Variables
- **Binary variables:** `assignments[(staff_id, patient_id, time)]`
- Value = 1 if staff member is assigned to patient at that time slot
- Value = 0 otherwise

### Time Slots
- 12 hourly blocks per shift (indexed 0-11)
- **Day shift:** 08:00-19:00 (slots 0-11)
- **Night shift:** 20:00-07:00 (slots 0-11)

---

## Constraint Categories

### 1. PATIENT OBSERVATION LEVEL REQUIREMENTS (Hard Constraints)

These are **equality constraints** that MUST be satisfied for any valid solution.

#### 1.1 Level 0 (General Observations)
```
Constraint: No staff assignment required
Implementation: assignments[staff, patient, time] = 0
```
**Rationale:** Patients on general observations don't need dedicated observation staff.

#### 1.2 Level 1 (1:1 Observations)
```
Constraint: Sum of all staff assigned to patient at time = 1
Implementation: Σ(assignments[s, patient, t]) = 1  for all t
```
**Rationale:** Exactly one staff member must observe the patient at all times.

#### 1.3 Level 2 (2:1 Observations)
```
Constraint: Sum of all staff assigned to patient at time = 2
Implementation: Σ(assignments[s, patient, t]) = 2  for all t
```
**Rationale:** Exactly two staff members must observe the patient simultaneously.

#### 1.4 Level 3 (3:1 Observations)
```
Constraint: Sum of all staff assigned to patient at time = 3
Implementation: Σ(assignments[s, patient, t]) = 3  for all t
```
**Rationale:** Exactly three staff members must observe the patient simultaneously.

#### 1.5 Level 4 (4:1 Observations)
```
Constraint: Sum of all staff assigned to patient at time = 4
Implementation: Σ(assignments[s, patient, t]) = 4  for all t
```
**Rationale:** Exactly four staff members must observe the patient simultaneously.

---

### 2. GENDER REQUIREMENTS (Hard Constraints)

#### 2.1 Gender Matching
```
Constraint: If patient requires male staff, exclude female staff (and vice versa)
Implementation: 
  IF patient.gender_req = 'M' AND staff.gender = 'F':
    assignments[staff, patient, time] = 0  for all t
  IF patient.gender_req = 'F' AND staff.gender = 'M':
    assignments[staff, patient, time] = 0  for all t
```
**Rationale:** Some patients require same-gender or opposite-gender staff for cultural, safety, or comfort reasons.

**Example:** Female patient requesting only female staff for intimate care observations.

---

### 3. STAFF AVAILABILITY CONSTRAINTS (Hard Constraints)

#### 3.1 Assigned Status
```
Constraint: Only staff marked as "assigned" can be allocated
Implementation:
  IF staff.assigned = False:
    assignments[staff, patient, time] = 0  for all patients, all times
```
**Rationale:** Staff who are not working the shift (off-duty, sick, on break for entire shift) should not be allocated.

**UI Control:** Checkbox in Staff page "Assign" column.

#### 3.2 Working Hours
```
Constraint: Staff can only be assigned during their scheduled hours
Implementation:
  IF time < staff.start_time OR time >= staff.end_time:
    assignments[staff, patient, time] = 0
```
**Rationale:** Staff have defined shift start and end times. Can't assign someone who isn't present.

**Example:** Staff working 08:00-13:00 (start_time=0, end_time=5) can only be assigned to slots 0-4.

**UI Control:** "Start" and "End" time columns in Staff page.

#### 3.3 Omit Times (Staff-Specific Breaks)
```
Constraint: Staff cannot be assigned at specifically omitted times
Implementation:
  FOR each time in staff.omit_time:
    assignments[staff, patient, time] = 0  for all patients
```
**Rationale:** Staff may have scheduled breaks, meetings, or other commitments at specific times.

**Example:** Staff member has lunch break at 13:00 and 14:00.

**UI Control:** "Omit" column in Staff page (format: "13:00 14:00").

---

### 4. STAFF-PATIENT EXCLUSION CONSTRAINTS (Hard Constraints)

#### 4.1 Patient-Requested Staff Exclusions
```
Constraint: Specific staff cannot be assigned to specific patients
Implementation:
  IF staff.name in patient.omit_staff:
    assignments[staff, patient, time] = 0  for all times
```
**Rationale:** Patients may request specific staff not be assigned to them due to relationship issues, previous incidents, or personal preference.

**Example:** Patient requests not to have "John Smith" as their observer.

**UI Control:** "Selector" and "Omit Staff" columns in Patient page.

#### 4.2 Staff Special List (Cherry-Picking)
```
Constraint: Staff with a special_list can ONLY be assigned to patients in that list
Implementation:
  IF staff.special_list is not empty AND patient.name NOT in staff.special_list:
    assignments[staff, patient, time] = 0  for all times
```
**Rationale:** Some staff may be specially trained or designated for specific patients (e.g., trauma-informed care, specific medical training).

**Example:** Staff member "Jane Doe" is specially trained and should only observe "Patient A" and "Patient B".

**UI Control:** "Selector" and "Cherry Pick" columns in Staff page.

---

### 5. WORKLOAD DISTRIBUTION CONSTRAINTS (Hard Constraints)

#### 5.1 One Patient Per Staff at Any Time
```
Constraint: Each staff can observe at most one patient at any given time
Implementation:
  Σ(assignments[staff, p, time]) ≤ 1  for all patients p, for each time
```
**Rationale:** Staff cannot physically observe multiple patients simultaneously (exception: for 2:1, 3:1, 4:1, multiple staff observe the same patient, but each staff still observes only one patient).

---

### 6. CONSECUTIVE HOURS CONSTRAINTS (Hard Constraints)

#### 6.1 Maximum Consecutive Hours Per Patient
```
Constraint: No staff assigned to same patient for more than 2 consecutive hours
Implementation:
  FOR each 3-hour sliding window [t-1, t, t+1]:
    Σ(assignments[staff, patient, t']) ≤ 2  for t' in window
```
**Rationale:** Prevents staff fatigue and maintains alertness. Staff need breaks from intensive observation work.

**Example:** Staff observing Patient A at hours 0,1 cannot be assigned to Patient A at hour 2. But they CAN be assigned to Patient B at hour 2.

**Note:** This constraint applies **per patient**, not globally. Staff can switch between patients.

---

### 7. MANDATORY BREAK CONSTRAINTS (Hard Constraints)

These ensure staff get adequate rest during their shifts.

#### 7.1 Short Shift Breaks (Duration < 12 hours)
```
Constraint: Must have at least 1 unassigned hour in any 2-hour window after first 3 hours
Implementation:
  FOR t from (start_time + 3) to end_time:
    Σ(assignments[staff, all patients, t']) ≤ 1  for t' in [t-1, t]
```
**Rationale:** Shorter shifts (6-11 hours) need periodic breaks. After working 3 hours, must have at least 1 break hour in every 2-hour period.

**Example:** 6-hour shift (08:00-13:00): After hour 3, must have breaks spread throughout remaining hours.

#### 7.2 Long Shift Breaks (Duration ≥ 12 hours)
```
Constraint: Must have at least 2 unassigned hours between slots 5-11
Implementation:
  Σ(assignments[staff, all patients, t]) ≤ 5  for t in range(5, 12)
```
**Rationale:** Long 12-hour shifts require substantial break time. In the 7-hour period from slot 5 to 11, staff can work maximum 5 hours, ensuring at least 2 hours of breaks.

**Example:** Long day shift 08:00-19:00: Must have at least 2 hours off between 13:00-19:00 (slots 5-11).

---

## Constraint Summary Table

| # | Constraint Type | Nature | Scope | Purpose |
|---|----------------|--------|-------|---------|
| 1 | Observation Levels 0-4 | Hard (=) | Patient-Time | Ensure correct staff-to-patient ratios |
| 2 | Gender Requirements | Hard (=0) | Staff-Patient | Respect patient gender preferences |
| 3.1 | Assigned Status | Hard (=0) | Staff-All | Only include working staff |
| 3.2 | Working Hours | Hard (=0) | Staff-Time | Staff only work their shift hours |
| 3.3 | Omit Times | Hard (=0) | Staff-Time | Respect scheduled breaks/meetings |
| 4.1 | Omit Staff | Hard (=0) | Staff-Patient | Respect patient exclusion requests |
| 4.2 | Special List | Hard (=0) | Staff-Patient | Restrict staff to designated patients |
| 5.1 | One Patient Per Time | Hard (≤1) | Staff-Time | No double-booking of staff |
| 6.1 | Consecutive Hours | Hard (≤2) | Staff-Patient-Window | Prevent observation fatigue |
| 7.1 | Short Shift Breaks | Hard (≤1) | Staff-Window | Ensure regular breaks |
| 7.2 | Long Shift Breaks | Hard (≤5) | Staff-Range | Ensure substantial break time |

**Total Constraint Types:** 11 categories
**All constraints are HARD constraints** (must be satisfied for feasibility)

---

## Objective Function

```
Minimize: max_workload
```

Where `max_workload` is defined as:
```
For each staff s:
  total_workload[s] ≤ max_workload
  total_workload[s] = Σ(assignments[s, o, t] for all observations o, times t)
```

**Rationale:** The solver now uses **min-max optimization** to balance workload fairly across all staff members. By minimizing the maximum workload (the busiest staff member's hours), the solver naturally distributes work as evenly as possible while still satisfying all hard constraints.

**Benefits:**
- Fair distribution of observation duties
- Prevents staff burnout
- Reduces workload imbalance
- Improves staff morale

**Example:** With 3 staff and 6 hours of work, instead of assigning 6-0-0, the optimizer finds 2-2-2.

See `WORKLOAD_OPTIMIZATION.md` for detailed explanation and examples.

---

## Feasibility Considerations

A problem becomes **INFEASIBLE** when constraints cannot all be satisfied simultaneously. Common causes:

### 1. Insufficient Staff Hours
- **Issue:** Total staff hours < total required observation hours
- **Example:** 1 patient needing 1:1 for 12 hours, but only 10 staff-hours available
- **Solution:** Add more staff or reduce observation levels

### 2. Gender Constraint Conflicts
- **Issue:** Patient requires specific gender, but no staff of that gender available
- **Example:** Patient requires female staff, but all assigned staff are male
- **Solution:** Assign staff of required gender or remove gender requirement

### 3. Conflicting Special Lists / Omit Staff
- **Issue:** Only staff who can observe a patient are excluded by that patient
- **Example:** Only "Jane" can observe "Patient A" (special_list), but "Patient A" excludes "Jane" (omit_staff)
- **Solution:** Reconcile exclusions or add alternative staff

### 4. Over-Constrained Breaks with Continuous Coverage
- **Issue:** Break requirements make continuous coverage impossible
- **Example:** 2 patients need 1:1, but each of 2 staff must take breaks, leaving gaps
- **Solution:** Add more staff to cover break periods

### 5. Consecutive Hours Impossible
- **Issue:** Continuous coverage needed but consecutive hours constraint prevents it
- **Example:** 1 staff, 1 patient, 12 hours needed, but max 2 consecutive hours allowed
- **Solution:** Add more staff to rotate assignments

---

## Solver Output

### On Success
- Returns assignment dictionary with values 0 or 1
- Generates allocation tables showing staff-to-patient assignments
- Produces downloadable CSV and PDF reports

### On Infeasibility
- Prints "Status: Infeasible"
- No valid allocation is generated
- User should run the feasibility pre-check or diagnostic tool to identify issues

---

## Pre-Solve Feasibility Check

Before solving, the system runs `check_allocation_feasibility()` which performs a simplified check:

```python
For each hour:
    required_staff = sum of all patient observation levels
    available_staff = count of assigned staff available at that hour
    if available_staff < required_staff:
        return INFEASIBLE with warning
```

This catches obvious infeasibilities before running the full solver.

---

## Configuration Requirements for Valid Solutions

### Minimum Requirements
1. ✅ At least 1 staff marked as "assigned" = True
2. ✅ Staff have valid time ranges (start_time < end_time)
3. ✅ At least 1 patient with observation_level > 0
4. ✅ Total staff-hours ≥ total observation-hours needed

### Recommended Best Practices
1. 📊 Staff-to-patient ratio of at least 1.5:1 for buffer
2. 🕐 Stagger staff start/end times to cover break periods
3. 👥 Have staff of both genders if gender requirements exist
4. 🔄 Plan for at least 3-4 staff per patient for rotation on long shifts
5. ⚠️ Use feasibility pre-check before attempting to solve

---

## Related Documentation
- `SOLVER_FIXES.md` - Details on recent bug fixes and improvements
- `DATABASE_FIX_REPORT.md` - Guide for fixing database configuration issues
- `diagnose_and_fix_db.py` - Automated diagnostic and repair tool
- `README.md` - General application overview

