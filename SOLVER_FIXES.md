# Solver Functionality Review and Fixes

## Issues Found and Resolved

### 1. **Double Solve Bug** ✅ FIXED
**Problem:** The solver was calling `problem.solve()` twice (lines 163 and 166), with the second call overwriting the first.

**Impact:** Inefficient and potentially confusing behavior; the first solve result was discarded.

**Fix:** Removed the redundant first `problem.solve()` call and kept only the one with logging parameters.

```python
# Before:
problem.solve()
solve = problem.solve(PULP_CBC_CMD(logPath="log.txt", keepFiles=True, msg=True))

# After:
problem.solve(PULP_CBC_CMD(logPath="log.txt", keepFiles=True, msg=True))
```

---

### 2. **Objective Function Issue** ✅ FIXED
**Problem:** The objective function was trying to minimize `1 - assignments[...]`, which was intended to minimize unassigned observations. However, since the observation level constraints are hard equalities (e.g., level 1 must have exactly 1 staff), the solution is fully determined by constraints, making the objective meaningless.

**Impact:** The objective was computing over fully constrained variables, adding unnecessary complexity without affecting the solution.

**Fix:** Replaced with a dummy objective (minimize 0) since the problem is a pure feasibility problem with hard constraints.

```python
# Before:
problem += pulp.lpSum(
    [1 - assignments[(s["id"], o["id"], t)] for o in observations for t in range(12) for s in staff if
     s["assigned"] and s["start_time"] <= t < s["end_time"]]), "Minimize Unassigned Observations"

# After:
problem += 0, "Feasibility_Objective"
```

---

### 3. **Consecutive Hours Constraint Bug** ✅ FIXED
**Problem:** The constraint was limiting consecutive assignments across ALL patients instead of per patient. The original constraint said: "Sum of all assignments for staff S across all patients in a 3-hour window must be ≤ 2."

**Impact:** This made the problem infeasible in realistic scenarios. With 2 staff covering 2 patients continuously, staff couldn't switch between patients without violating the constraint.

**Example:** If S1 covers P1 at times 0,1 and then P2 at time 2, the window [0,1,2] would have 3 total assignments, violating the ≤2 constraint even though S1 only covered each patient for 2 consecutive hours.

**Fix:** Changed the constraint to apply per patient, meaning staff cannot be assigned to THE SAME patient for more than 2 consecutive hours.

```python
# Before (wrong - sums across all patients):
for s in staff:
    for t in range(11):
        if s["assigned"] and s["start_time"] <= t < s["end_time"] - 1:
            problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] 
                                   for o in observations 
                                   for t_prime in range(max(0, t - 1), t + 2)]) <= 2

# After (correct - applies per patient):
for s in staff:
    for o in observations:
        for t in range(11):
            if s["assigned"] and s["start_time"] <= t < s["end_time"] - 1:
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] 
                                       for t_prime in range(max(0, t - 1), t + 2)]) <= 2
```

---

### 4. **Special List Constraint Implementation** ✅ VERIFIED WORKING
**Problem:** The original special_list constraint was using Python conditionals on decision variables, which doesn't create proper LP constraints.

**Fix:** Already corrected in quick wins to create proper linear constraints:

```python
for s in staff:
    special = set(s.get("special_list") or [])
    if special:
        for o in observations:
            if o["name"] not in special:
                for t in range(12):
                    problem += assignments[(s["id"], o["id"], t)] == 0
```

This ensures that if a staff member has a non-empty special_list, they can ONLY be assigned to patients in that list.

---

### 5. **Streamlit Coupling in Solver** ✅ FIXED
**Problem:** The solver imported and used Streamlit (`st.write`) and called `exit()` on infeasible solutions, making it untestable and coupling business logic to UI.

**Fix:** Removed Streamlit import from solver, replaced with print statement, and removed exit() call.

```python
# Before:
import streamlit as st
...
if pulp.LpStatus[problem.status] == 'Infeasible':
    st.write(f"**:red[Status: {pulp.LpStatus[problem.status]}]**")
    exit()

# After:
if pulp.LpStatus[problem.status] == 'Infeasible':
    print(f"Status: {pulp.LpStatus[problem.status]}")
```

---

## Test Coverage Added

### New Solver Tests (`solver/test_milo_solve.py`)
1. **`test_special_list_enforced`**: Verifies that staff with a special_list are only assigned to patients in that list.
2. **`test_basic_feasibility`**: Verifies that a simple feasible scenario (1 staff, 1 patient, short duration) produces a valid solution.

All tests now pass successfully:
- 2 new solver tests ✅
- 7 existing service tests ✅

---

## Key Insights

### Why Tests Were Initially Failing
The test scenarios were **mathematically infeasible** due to the combination of:
1. Continuous coverage requirements (2 patients needing 1:1 for 12 hours)
2. Limited staff (only 2 staff available)
3. Mandatory break constraints (staff with 12-hour shifts need 2 hours break)
4. Maximum consecutive hours (no more than 2 consecutive hours per patient)

**Example infeasibility:** If S1 must only cover P2 (special_list), then S2 must cover P1 for all 12 hours. But the break constraint requires S2 to have at least 2 hours off in slots 5-11, leaving P1 uncovered during those times.

### Solution
Updated tests to use realistic, feasible scenarios:
- Shorter durations (avoiding break constraints)
- Single patient coverage when testing special_list constraints
- Observation level 0 (no coverage needed) for patients that shouldn't be assigned

---

## Recommendations for Future Enhancements

### 1. Soft Constraints for Break Periods
Consider making break constraints "soft" (penalty-based) rather than hard requirements, allowing the solver to find solutions that violate breaks if necessary, with a preference to respect them.

### 2. Infeasibility Reporting
Add structured infeasibility detection and reporting:
```python
if pulp.LpStatus[problem.status] == 'Infeasible':
    return {
        'success': False,
        'status': 'Infeasible',
        'message': 'No valid allocation found. This may be due to insufficient staff, conflicting constraints, or impossible coverage requirements.',
        'staff': staff,
        'observations': observations,
        'assignments': None
    }
```

### 3. Objective Function Options
Consider adding alternative objectives when the problem is feasible but has flexibility:
- Minimize workload imbalance across staff
- Maximize consecutive assignments (fewer context switches)
- Minimize total break time deviations
- Prefer certain staff-patient pairings

### 4. Validation Pre-Check
Add a fast pre-check before solving:
```python
def quick_feasibility_check(staff, patients):
    """Check if basic coverage requirements can be met."""
    total_demand = sum([int(p['observation_level']) for p in patients]) * 12
    total_supply = sum([s['end_time'] - s['start_time'] for s in staff if s['assigned']])
    if total_demand > total_supply:
        return False, f"Insufficient staff hours: need {total_demand}, have {total_supply}"
    return True, "Basic requirements met"
```

---

## Files Modified

1. `solver/milo_solve.py` - Fixed double solve, objective function, consecutive hours constraint, removed Streamlit
2. `solver/test_milo_solve.py` - Added comprehensive tests with feasible scenarios
3. All service tests continue to pass ✅

## Summary

The solver now correctly implements the intended constraints and can be tested independently of the UI. The main issue was the consecutive hours constraint applying globally across all patients rather than per-patient, which made most realistic scenarios infeasible.

