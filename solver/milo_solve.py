 # milo_solve.py

import os
import sys

from pulp import PULP_CBC_CMD

# add the path to the custom module to the system's path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pulp
from database_utils.milo_input_data import get_staff_rows_as_dict, get_patient_rows_as_dict
from .milo_results import print_results
import streamlit as st


def handle_infeasibility(staff, observations, shift):
    """
    Display helpful diagnostics when the solver reports infeasibility.
    """
    st.error("❌ Allocation Problem is INFEASIBLE")
    st.markdown("---")
    
    st.markdown("### The allocation cannot be solved with current constraints.")
    st.markdown("This means it's mathematically impossible to satisfy all requirements simultaneously.")
    
    # Analyze the issue
    st.markdown("### 🔍 Diagnostic Analysis")
    
    # Count staff with 12h shifts
    staff_12h = [s for s in staff if s.get("assigned") and s.get("duration", 0) >= 12]
    staff_less_12h = [s for s in staff if s.get("assigned") and s.get("duration", 0) < 12]
    
    # Calculate observation needs
    total_need_per_slot = sum(int(o.get("observation_level", 0)) for o in observations)
    
    st.markdown(f"""
    **Current Staffing:**
    - 🕐 **{len(staff_12h)} staff** working ≥12 hour shifts (need 2-hour breaks in slots 5-11)
    - 🕑 **{len(staff_less_12h)} staff** working <12 hour shifts
    - 📊 **{total_need_per_slot} staff** needed per hour for observations
    """)
    
    # Break window analysis
    if len(staff_12h) > 0:
        capacity_in_break_window = len(staff_12h) * 5  # max 5 of 7 slots
        required_in_break_window = total_need_per_slot * 7  # 7 slots
        
        st.markdown(f"""
        **Break Window Analysis (Slots 5-11):**
        - 🔢 Available capacity: {len(staff_12h)} staff × 5 slots = **{capacity_in_break_window} staff-slots**
        - 📋 Required coverage: {total_need_per_slot} staff × 7 slots = **{required_in_break_window} staff-slots**
        """)
        
        if capacity_in_break_window < required_in_break_window:
            shortage = required_in_break_window - capacity_in_break_window
            st.error(f"⚠️ **SHORTAGE: {shortage} staff-slots** in break window!")
    
    # Recommendations
    st.markdown("### 💡 Recommended Solutions")
    
    with st.expander("✅ Solution 1: Add More Staff (Easiest)", expanded=True):
        if len(staff_12h) > 0:
            capacity_in_break_window = len(staff_12h) * 5
            required_in_break_window = total_need_per_slot * 7
            if capacity_in_break_window < required_in_break_window:
                shortage = required_in_break_window - capacity_in_break_window
                additional_needed = (shortage + 4) // 5  # Round up
                st.markdown(f"""
                Add **{additional_needed} more staff members** working 12-hour shifts.
                
                **Steps:**
                1. Go to the **Staff** tab
                2. Add {additional_needed} new staff members
                3. Set them as "Assigned" 
                4. Set working hours: 08:00-19:00 (full day shift)
                5. Return here and re-run allocations
                """)
    
    with st.expander("✅ Solution 2: Stagger Shift Times"):
        st.markdown("""
        Change some staff to **11-hour shifts** instead of 12-hour shifts.
        
        **Why this helps:** 11-hour shifts only require a 1-hour break (more flexible).
        
        **Steps:**
        1. Go to the **Staff** tab
        2. Select 3-4 staff members
        3. Change their end time from 19:00 to 18:00 (11-hour shift)
        4. Return here and re-run allocations
        """)
    
    with st.expander("✅ Solution 3: Reduce Observation Levels"):
        high_obs_patients = [o for o in observations if int(o.get("observation_level", 0)) >= 2]
        if high_obs_patients:
            st.markdown(f"""
            You have **{len(high_obs_patients)} patient(s)** with level-2 or higher observations.
            
            If clinically appropriate, consider reducing observation levels temporarily:
            
            **Steps:**
            1. Go to the **Patients** tab
            2. Review high-observation patients
            3. Adjust observation levels if appropriate
            4. Return here and re-run allocations
            """)
        else:
            st.markdown("""
            Consider reducing observation levels for some patients during the afternoon (if clinically appropriate).
            """)
    
    st.markdown("---")
    st.info("💡 **Tip:** Start with Solution 1 (add more staff) - it's the quickest fix!")


def solve_staff_allocation(shift):
    # Define input data
    staff = get_staff_rows_as_dict()
    observations = get_patient_rows_as_dict()

    # Create a new optimization problem
    problem = pulp.LpProblem("Staff_Observation_Assignment_Problem", pulp.LpMinimize)

    # Define the decision variables
    assignments = pulp.LpVariable.dicts("Assignments",
                                        ((s["id"], o["id"], t) for s in staff for o in observations for t in range(12)),
                                        cat="Binary")

    # Patients whose observation level == 0 may be ignored
    for o in observations:
        if o["observation_level"] == "0":
            for s in staff:
                for t in range(12):
                    problem += assignments[(s["id"], o["id"],
                                            t)] == 0, f"Ignore Observation (observation {o['id']}, staff {s['id']}, time {t}) Constraint"

    # Patients whose observation level == 1 must be assigned 1 staff for each time
    for o in observations:
        if o["observation_level"] == "1":
            for t in range(12):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t)] for s in
                                       staff]) == 1, f"Observation Level 1 (observation {o['id']}, time {t}) Constraint"

    # Patients whose observation level == 2 must be assigned 2 staff for each time
    for o in observations:
        if o["observation_level"] == "2":
            for t in range(12):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t)] for s in
                                       staff]) == 2, f"Observation Level 2 (observation {o['id']}, time {t}) Constraint"

    # Patients whose observation level == 3 must be assigned 3 staff for each time
    for o in observations:
        if o["observation_level"] == "3":
            for t in range(12):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t)] for s in
                                       staff]) == 3, f"Observation Level 3 (observation {o['id']}, time {t}) Constraint"

    # Patients whose observation level == 4 must be assigned 4 staff for each
    # time
    for o in observations:
        if o["observation_level"] == "4":
            for t in range(12):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t)] for s in
                                       staff]) == 4, f"Observation Level 4 (observation {o['id']}, time {t}) Constraint"

    # If gender_req == M staff whose gender == F must not be assigned any time
    # for that patient If gender_req == F staff whose gender == M must not be
    # assigned any time for that patient
    for o in observations:
        for s in staff:
            if (o["gender_req"] == "M" and s["gender"] == "F") or (o["gender_req"] == "F" and s["gender"] == "M"):
                for t in range(12):
                    problem += assignments[(s["id"], o["id"],
                                            t)] == 0, f"Gender Constraint (observation {o['id']}, staff {s['id']}, time {t}) Constraint"

    # Ignore staff if assigned==False
    for s in staff:
        if not s["assigned"]:
            for t in range(12):
                for o in observations:
                    problem += assignments[(
                        s["id"], o["id"], t)] == 0, f"Unassigned_Staff_(staff_{s['id']})_Constraint_o={o['id']}_t={t}"

    # Staff must only be assigned from their start_time to end_time
    for s in staff:
        for t in range(12):
            if t < s["start_time"] or t >= s["end_time"]:
                for o in observations:
                    problem += assignments[(s["id"], o["id"],
                                            t)] == 0, f"Staff_Time_Availability_(staff_{s['id']},_observation_{o['id']},_time_{t})_Constraint"

    # Ensure staff are not assigned at specific times
    for s in staff:
        if 'omit_time' in s:
            for t in s['omit_time']:
                for o in observations:
                    problem += assignments[(s["id"], o["id"],
                                            t)] == 0, f"Omit Time (staff {s['id']}, observation {o['id']}, time {t}) Constraint"

    # Names in omit_staff must not be assigned any time for that patient
    for o in observations:
        for s in staff:
            if s["name"] in o["omit_staff"]:
                for t in range(12):
                    problem += assignments[(
                        s["id"], o["id"],
                        t)] == 0, f"Omit Staff (observation {o['id']}, staff {s['id']}, time {t}) Constraint"

    # Enforce staff are only assigned to patients in their special_list (if any)
    for s in staff:
        special = set(s.get("special_list") or [])
        if special:
            for o in observations:
                if o["name"] not in special:
                    for t in range(12):
                        problem += assignments[(s["id"], o["id"], t)] == 0, \
                            f"Special List Restriction (staff {s['id']}, observation {o['id']}, time {t}) Constraint"

    # Ensure staff are assigned to no more than one patient at a time
    for t in range(12):
        for s in staff:
            # Create a list of patients assigned to the current staff at the
            # current time
            assigned_patients = [assignments[(s["id"], o["id"], t)] for o in observations]
            # Add a constraint that the sum of the assigned_patients list
            # must be less than or equal to 1
            problem += pulp.lpSum(
                assigned_patients) <= 1, f"Staff Row Constraint (staff {s['id']}, time {t}) Constraint"

    # Ensure each staff member is not assigned to THE SAME observation for more
    # than 2 consecutive hours
    for s in staff:
        for o in observations:
            for t in range(11):
                if s["assigned"] and s["start_time"] <= t < s["end_time"] - 1:
                    problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] for t_prime in
                                           range(max(0, t - 1),
                                                 t + 2)]) <= 2, f"Consecutive Hours (staff {s['id']}, observation {o['id']}, time {t}) Constraint"

    # Staff whose duration is < 12 must have >= 1 unassigned time slot
    # between their start_time + 3 and end_time
    for s in staff:
        if s["duration"] < 12:
            for t in range(s["start_time"] + 3, s["end_time"]):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] for o in observations for t_prime in
                                       range(t - 1,
                                             t + 1)]) <= 1, f"Minimum Break (staff {s['id']}, time {t}) Constraint"

    # Staff whose duration is >= 12 must have >= 2 unassigned time slots
    # between 5 and 11
    for s in staff:
        if s["duration"] >= 12:
            problem += pulp.lpSum(
                [assignments[(s["id"], o["id"], t)] for o in observations for t in range(5, 12)]) <= 5, \
                f"Break Constraint (staff {s['id']}) Constraint"

    # Add the objective function to minimize workload imbalance
    # We minimize the maximum workload (min-max optimization) to ensure fair distribution
    
    # Create auxiliary variable for maximum workload
    max_workload = pulp.LpVariable("max_workload", lowBound=0, cat="Continuous")
    
    # For each staff member, calculate their total workload and constrain it to be <= max_workload
    for s in staff:
        if s["assigned"]:  # Only consider assigned staff
            staff_total_workload = pulp.lpSum([assignments[(s["id"], o["id"], t)] 
                                               for o in observations 
                                               for t in range(12)
                                               if s["start_time"] <= t < s["end_time"]])
            problem += staff_total_workload <= max_workload, f"Max_Workload_Constraint_Staff_{s['id']}"
    
    # Objective: minimize the maximum workload (this tends to balance workload across staff)
    problem += max_workload, "Minimize_Maximum_Workload"

    # Solve the problem with logging enabled
    problem.solve(PULP_CBC_CMD(logPath="log.txt", keepFiles=True, msg=True))
    problem.writeLP('allocations.lp')

    # Check solver status and handle infeasibility
    status = pulp.LpStatus[problem.status]
    
    if status == 'Infeasible':
        print(f"Status: {status}")
        handle_infeasibility(staff, observations, shift)
        return None, None, None
    elif status == 'Optimal':
        st.success(f"✅ Allocation Status: {status}")
        print_results(staff, observations, assignments, shift)
        return staff, observations, assignments
    else:
        st.warning(f"⚠️ Allocation Status: {status}")
        print_results(staff, observations, assignments, shift)
        return staff, observations, assignments

