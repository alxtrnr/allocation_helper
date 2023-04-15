# milo_solve.py

import os
import sys

from pulp import PULP_CBC_CMD

# add the path to the custom module to the system's path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pulp
import streamlit as st
from database_utils.milo_input_data import get_staff_rows_as_dict, get_patient_rows_as_dict
from .milo_results import print_results


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

    # Patients whose observation level == 4 must be assigned 4 staff for each time
    for o in observations:
        if o["observation_level"] == "4":
            for t in range(12):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t)] for s in
                                       staff]) == 4, f"Observation Level 4 (observation {o['id']}, time {t}) Constraint"

    # If gender_req == M staff whose gender == F must not be assigned any time for that patient
    # If gender_req == F staff whose gender == M must not be assigned any time for that patient
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
            if s["id"] in o["omit_staff"]:
                for t in range(12):
                    problem += assignments[(
                        s["id"], o["id"],
                        t)] == 0, f"Omit Staff (observation {o['id']}, staff {s['id']}, time {t}) Constraint"

    # Ensure staff are only assigned to a specific patient(s)
    for s in staff:
        for o in observations:
            if o["name"] in s["cherry_pick"]:
                for t in range(12):
                    if assignments[(s["id"], o["id"], t)] == 1:
                        # set all other assignments for this staff to 0 for this time slot
                        for other_o in observations:
                            if other_o != o and (s["id"], other_o["id"], t) in assignments:
                                problem += assignments[(s["id"], other_o["id"], t)] == 0

    # Ensure staff are assigned to no more than one patient at a time
    for t in range(12):
        for s in staff:
            # Create a list of patients assigned to the current staff at the current time
            assigned_patients = [assignments[(s["id"], o["id"], t)] for o in observations]
            # Add a constraint that the sum of the assigned_patients list must be less than or equal to 1
            problem += pulp.lpSum(
                assigned_patients) <= 1, f"Staff Row Constraint (staff {s['id']}, time {t}) Constraint"

    # Ensure each staff member is not assigned to an observation for more than 2 consecutive hours
    for s in staff:
        for t in range(11):
            if s["assigned"] and s["start_time"] <= t < s["end_time"] - 1:
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] for o in observations for t_prime in
                                       range(max(0, t - 1),
                                             t + 2)]) <= 2, f"Consecutive Hours (staff {s['id']}, time {t}) Constraint"

    # Staff whose duration is < 12 must have >= 1 unassigned time slot between their start_time + 3 and end_time
    for s in staff:
        if s["duration"] < 12:
            for t in range(s["start_time"] + 3, s["end_time"]):
                problem += pulp.lpSum([assignments[(s["id"], o["id"], t_prime)] for o in observations for t_prime in
                                       range(t - 1,
                                             t + 1)]) <= 1, f"Minimum Break (staff {s['id']}, time {t}) Constraint"

    # Staff whose duration is >= 12 must have >= 2 unassigned time slots between 5 and 11
    for s in staff:
        if s["duration"] >= 12:
            problem += pulp.lpSum(
                [assignments[(s["id"], o["id"], t)] for o in observations for t in range(5, 12)]) <= 5, \
                f"Break Constraint (staff {s['id']}) Constraint"

    # Add the objective function to the problem
    problem += pulp.lpSum(
        [1 - assignments[(s["id"], o["id"], t)] for o in observations for t in range(12) for s in staff if
         s["assigned"] and s["start_time"] <= t < s[
             "end_time"]]), "Minimize Unassigned Observations"

    # Solve the problem
    problem.solve()
    # set the logPath and keepFiles parameters to create a log of the MIP formulation
    solve = problem.solve(PULP_CBC_CMD(logPath="log.txt", keepFiles=True, msg=True))
    problem.writeLP('allocations.lp')

    # Print the status of the solution
    st.write("Status:", pulp.LpStatus[problem.status])
    if pulp.LpStatus[problem.status] == 'Infeasible':
        exit('You need more staff!')

    print_results(staff, observations, assignments, shift)
    return staff, observations, assignments

