import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from models import init_in_memory_db
from services.staff_service import add_staff_entry, delete_staff_entry, update_staff_entry, check_allocation_feasibility

def setup_test_db():
    Session, StaffTable, _ = init_in_memory_db()
    return Session, StaffTable

def test_add_staff_basics():
    Session, StaffTable = setup_test_db()
    session = Session()
    result = add_staff_entry(session, name='John Doe', role='HCA', gender='M')
    session.commit()
    assert result['success']
    assert session.query(StaffTable).filter_by(name='John Doe'.title()).one_or_none() is not None
    result2 = add_staff_entry(session, name='John Doe', role='HCA', gender='M')
    session.commit()
    assert not result2['success']
    assert 'already exists' in result2['message']
    result3 = add_staff_entry(session, name='', role='HCA', gender='M')
    session.commit()
    assert not result3['success']
    result4 = add_staff_entry(session, name='Jane Smith', role='HCA', gender='X')
    session.commit()
    assert not result4['success']
    session.close()

def test_update_staff():
    Session, StaffTable = setup_test_db()
    session = Session()
    result = add_staff_entry(session, name='Original Name', role='HCA', gender='M')
    session.commit()
    staff = session.query(StaffTable).filter_by(name='Original Name'.title()).one_or_none()
    assert staff
    staff_id = staff.id
    # Change to valid new name
    update_result = update_staff_entry(session, staff_id, name='New Name', role='RMN', gender='F')
    session.commit()
    assert update_result['success']
    assert session.query(StaffTable).filter_by(name='New Name'.title()).one_or_none()
    # Try to update to duplicate name
    add_staff_entry(session, name='Other Staff', role='HCA', gender='M')
    session.commit()
    dup_result = update_staff_entry(session, staff_id, name='Other Staff')
    session.commit()
    assert not dup_result['success']
    # Try empty name
    empty_result = update_staff_entry(session, staff_id, name='')
    session.commit()
    assert not empty_result['success']
    # Try invalid gender
    bad_gender = update_staff_entry(session, staff_id, gender='X')
    session.commit()
    assert not bad_gender['success']
    # Try invalid role
    bad_role = update_staff_entry(session, staff_id, role='SURGEON')
    session.commit()
    assert not bad_role['success']
    session.close()

def test_delete_staff():
    Session, StaffTable = setup_test_db()
    session = Session()
    result = add_staff_entry(session, name='ToDelete', role='HCA', gender='F')
    session.commit()
    expected_name = 'ToDelete'.title()
    staff_obj = session.query(StaffTable).filter_by(name=expected_name).one_or_none()
    if staff_obj is None:
        print(f"Existing staff: {[s.name for s in session.query(StaffTable)]}")
    assert staff_obj is not None
    ok = delete_staff_entry(session, expected_name)
    session.commit()
    assert ok
    assert session.query(StaffTable).filter_by(name=expected_name).one_or_none() is None
    session.close()

def test_allocation_feasibility():
    Session, StaffTable = setup_test_db()
    from models import PatientTable
    session = Session()
    # Feasible: 2 staff, 2 obs 1:1
    add_staff_entry(session, name='A', role='HCA', gender='M', assigned=True)
    add_staff_entry(session, name='B', role='HCA', gender='F', assigned=True)
    # two patients with 1:1
    from services.patient_service import add_patient_entry
    add_patient_entry(session, name='p1', observation_level=1)
    add_patient_entry(session, name='p2', observation_level=1)
    session.commit()
    feas = check_allocation_feasibility(session)
    assert feas['success']
    # Infeasible: add a new patient with level 2, need 4 total for each time
    add_patient_entry(session, name='p3', observation_level=2)
    session.commit()
    feas2 = check_allocation_feasibility(session)
    assert not feas2['success']
    assert "shortfall" in ''.join(feas2['warnings'])
    session.close()
