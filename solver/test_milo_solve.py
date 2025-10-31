import pytest


def test_special_list_enforced(monkeypatch):
    # Prepare minimal in-memory data: 1 staff restricted to 1 specific patient
    staff = [
        {
            "id": 1,
            "name": "S1",
            "gender": "M",
            "assigned": True,
            "start_time": 0,
            "end_time": 4,
            "duration": 4,
            "omit_time": [],
            "special_list": ["P2"],
        },
    ]

    patients = [
        {
            "id": 10,
            "name": "P1",
            "gender_req": None,
            "observation_level": "0",  # Level 0 = no coverage needed
            "omit_staff": [],
            "obs_type": "standard",
            "room_number": "01",
        },
        {
            "id": 20,
            "name": "P2",
            "gender_req": None,
            "observation_level": "1",
            "omit_staff": [],
            "obs_type": "standard",
            "room_number": "02",
        },
    ]

    from solver import milo_solve

    monkeypatch.setattr(milo_solve, "get_staff_rows_as_dict", lambda: staff)
    monkeypatch.setattr(milo_solve, "get_patient_rows_as_dict", lambda: patients)

    _staff, _patients, assignments = milo_solve.solve_staff_allocation("D")

    # S1 must never be assigned to P1 due to special_list allowing only P2
    for t in range(12):
        assert assignments[(1, 10, t)].value() == 0 or assignments[(1, 10, t)].value() is None, \
            f"Staff 1 was assigned to Patient 1 at time {t}, violating special_list constraint"


def test_basic_feasibility(monkeypatch):
    # One 1:1 patient, one assigned staff with short duration (no break constraint) → feasible
    staff = [
        {"id": 1, "name": "S1", "gender": "M", "assigned": True, "start_time": 0, "end_time": 4, "duration": 4, "omit_time": [], "special_list": []},
    ]
    patients = [
        {"id": 10, "name": "P1", "gender_req": None, "observation_level": "1", "omit_staff": [], "obs_type": "standard", "room_number": "01"},
    ]

    from solver import milo_solve
    import pulp

    monkeypatch.setattr(milo_solve, "get_staff_rows_as_dict", lambda: staff)
    monkeypatch.setattr(milo_solve, "get_patient_rows_as_dict", lambda: patients)

    _staff, _patients, assignments = milo_solve.solve_staff_allocation("D")

    # Should be feasible: 1 staff covering 1 patient for 4 hours (no break needed)
    # Check the problem was actually solved successfully
    import pulp
    # The problem.status is stored in the assignments' problem reference, but we don't have direct access
    # Instead verify that assignments have valid values
    for t in range(4):
        val = assignments[(1, 10, t)].value()
        assert val is not None, f"Assignment at time {t} has no value - problem may be infeasible"
        assert val == 1.0, f"Expected staff 1 assigned to patient 1 at time {t}"


def test_workload_balancing(monkeypatch):
    """Test that workload is balanced across staff when possible."""
    # 3 staff, 1 patient needing 1:1 for 6 hours
    # Expected: workload should be distributed fairly (2 hours each ideally)
    staff = [
        {"id": 1, "name": "S1", "gender": "M", "assigned": True, "start_time": 0, "end_time": 6, "duration": 6, "omit_time": [], "special_list": []},
        {"id": 2, "name": "S2", "gender": "F", "assigned": True, "start_time": 0, "end_time": 6, "duration": 6, "omit_time": [], "special_list": []},
        {"id": 3, "name": "S3", "gender": "M", "assigned": True, "start_time": 0, "end_time": 6, "duration": 6, "omit_time": [], "special_list": []},
    ]
    patients = [
        {"id": 10, "name": "P1", "gender_req": None, "observation_level": "1", "omit_staff": [], "obs_type": "standard", "room_number": "01"},
    ]

    from solver import milo_solve

    monkeypatch.setattr(milo_solve, "get_staff_rows_as_dict", lambda: staff)
    monkeypatch.setattr(milo_solve, "get_patient_rows_as_dict", lambda: patients)

    _staff, _patients, assignments = milo_solve.solve_staff_allocation("D")

    # Calculate workload for each staff
    workloads = {}
    for s in staff:
        workload = 0
        for t in range(6):
            if assignments[(s["id"], 10, t)].value() == 1:
                workload += 1
        workloads[s["id"]] = workload
        print(f"Staff {s['id']} ({s['name']}): {workload} hours")

    # Verify all hours are covered
    for t in range(6):
        total = sum(assignments[(s["id"], 10, t)].value() for s in staff)
        assert total == 1.0, f"Hour {t} should have exactly 1 staff assigned"

    # Verify workload is balanced (max difference should be <= 1 for 6 hours / 3 staff)
    max_workload = max(workloads.values())
    min_workload = min(workloads.values())
    print(f"Workload range: {min_workload} to {max_workload}")
    
    # With 6 hours and 3 staff, ideal is 2 hours each
    # Allow some variation but should be fairly balanced
    assert max_workload <= 3, "No staff should work more than 3 hours"
    assert min_workload >= 1, "All staff should work at least 1 hour"
    assert max_workload - min_workload <= 1, "Workload should be balanced within 1 hour difference"


