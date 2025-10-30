import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from models import init_in_memory_db
from services.patient_service import add_patient_entry, delete_patient_entry, update_patient_entry

def setup_test_db():
    Session, StaffTable, PatientTable = init_in_memory_db()
    return Session, StaffTable, PatientTable

def test_add_patient_basics():
    Session, _, PatientTable = setup_test_db()
    session = Session()
    result = add_patient_entry(session, name='Alice Patient')
    session.commit()
    assert result['success']
    assert session.query(PatientTable).filter_by(name='Alice Patient'.title()).one_or_none() is not None
    result2 = add_patient_entry(session, name='Alice Patient')
    session.commit()
    assert not result2['success']
    result3 = add_patient_entry(session, name='')
    session.commit()
    assert not result3['success']
    session.close()

def test_update_patient():
    Session, _, PatientTable = setup_test_db()
    session = Session()
    add_patient_entry(session, name='Original Patient')
    session.commit()
    patient = session.query(PatientTable).filter_by(name='Original Patient'.title()).one_or_none()
    assert patient
    pid = patient.id
    # Valid changes
    res = update_patient_entry(session, pid, name='Updated Patient', observation_level=2, obs_type='arms-length', gender_req='F')
    session.commit()
    assert res['success']
    assert session.query(PatientTable).filter_by(name='Updated Patient'.title()).one_or_none()
    # Try to update to duplicate name
    add_patient_entry(session, name='Other Patient')
    session.commit()
    dup_res = update_patient_entry(session, pid, name='Other Patient')
    session.commit()
    assert not dup_res['success']
    # Empty
    empty_res = update_patient_entry(session, pid, name='')
    session.commit()
    assert not empty_res['success']
    session.close()

def test_delete_patient_and_remove_from_staff():
    Session, StaffTable, PatientTable = setup_test_db()
    session = Session()
    add_patient_entry(session, name='ToDeletePatient')
    session.commit()
    s = StaffTable(name='Doctor', role='HCA', gender='M', assigned=True, start_time=0, end_time=12, duration=12, special_list=['ToDeletePatient'.title()])
    session.add(s)
    session.commit()
    expected_name = 'ToDeletePatient'.title()
    assert session.query(PatientTable).filter_by(name=expected_name).one_or_none() is not None
    ok = delete_patient_entry(session, expected_name)
    session.commit()
    assert ok
    assert session.query(PatientTable).filter_by(name=expected_name).one_or_none() is None
    staff_fetched = session.query(StaffTable).filter_by(name='Doctor').first()
    assert staff_fetched
    assert expected_name not in staff_fetched.special_list
    session.close()
