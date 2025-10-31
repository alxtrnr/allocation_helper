"""
Test suite for staff data validation and auto-correction.

Tests ensure that the service layer properly validates and auto-corrects
staff data to maintain consistency between start_time, end_time, and duration.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, StaffTable
from services.staff_service import add_staff_entry, update_staff_entry

@pytest.fixture
def setup_test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_add_staff_auto_corrects_duration(setup_test_db):
    """Test that adding staff auto-corrects duration to match working hours."""
    session = setup_test_db
    
    # Try to add staff with mismatched duration
    result = add_staff_entry(
        session, 
        name="Test Staff",
        start_time=2,
        end_time=10,
        duration=12  # Wrong! Should be 8
    )
    
    assert result['success'] is True
    staff = session.query(StaffTable).filter_by(name="Test Staff").first()
    assert staff is not None
    assert staff.start_time == 2
    assert staff.end_time == 10
    assert staff.duration == 8  # Auto-corrected!

def test_add_staff_validates_time_range(setup_test_db):
    """Test that adding staff validates time ranges."""
    session = setup_test_db
    
    # Test invalid start time
    result = add_staff_entry(session, name="Staff1", start_time=-1, end_time=10)
    assert result['success'] is False
    assert 'Start time must be between 0 and 12' in result['message']
    
    # Test invalid end time
    result = add_staff_entry(session, name="Staff2", start_time=0, end_time=13)
    assert result['success'] is False
    assert 'End time must be between 0 and 12' in result['message']
    
    # Test start >= end
    result = add_staff_entry(session, name="Staff3", start_time=10, end_time=10)
    assert result['success'] is False
    assert 'End time must be greater than start time' in result['message']
    
    result = add_staff_entry(session, name="Staff4", start_time=10, end_time=8)
    assert result['success'] is False
    assert 'End time must be greater than start time' in result['message']

def test_update_staff_auto_corrects_duration(setup_test_db):
    """Test that updating staff times auto-corrects duration."""
    session = setup_test_db
    
    # Add a staff member
    result = add_staff_entry(session, name="Update Test", start_time=0, end_time=12)
    assert result['success'] is True
    staff = result['object']
    assert staff.duration == 12
    
    # Update to shorter hours with wrong duration
    result = update_staff_entry(
        session,
        staff.id,
        start_time=8,
        end_time=11,
        duration=12  # Wrong! Should be 3
    )
    
    assert result['success'] is True
    staff = session.query(StaffTable).get(staff.id)
    assert staff.start_time == 8
    assert staff.end_time == 11
    assert staff.duration == 3  # Auto-corrected!

def test_update_staff_corrects_duration_without_explicit_param(setup_test_db):
    """Test that updating times auto-corrects duration even when not explicitly provided."""
    session = setup_test_db
    
    # Add a staff member
    result = add_staff_entry(session, name="Auto Correct", start_time=0, end_time=12)
    staff = result['object']
    
    # Manually mess up the duration (simulating legacy data)
    staff.duration = 99
    session.commit()
    
    # Update end_time without providing duration parameter
    result = update_staff_entry(session, staff.id, end_time=6)
    
    assert result['success'] is True
    staff = session.query(StaffTable).get(staff.id)
    assert staff.end_time == 6
    assert staff.duration == 6  # Auto-corrected from 99 to 6!

def test_update_staff_validates_time_range(setup_test_db):
    """Test that updating staff validates time ranges."""
    session = setup_test_db
    
    result = add_staff_entry(session, name="Validate Test", start_time=2, end_time=10)
    staff = result['object']
    
    # Test invalid start time
    result = update_staff_entry(session, staff.id, start_time=-5)
    assert result['success'] is False
    assert 'Start time must be between 0 and 12' in result['message']
    
    # Test invalid end time
    result = update_staff_entry(session, staff.id, end_time=20)
    assert result['success'] is False
    assert 'End time must be between 0 and 12' in result['message']
    
    # Test start >= end after update
    result = update_staff_entry(session, staff.id, start_time=10)
    assert result['success'] is False
    assert 'End time must be greater than start time' in result['message']

def test_various_shift_lengths(setup_test_db):
    """Test that various shift lengths work correctly."""
    session = setup_test_db
    
    test_cases = [
        ("Short Shift", 0, 1, 1),
        ("Half Day", 0, 6, 6),
        ("Full Day", 0, 12, 12),
        ("Mid Day", 3, 9, 6),
        ("Evening", 8, 12, 4),
    ]
    
    for name, start, end, expected_duration in test_cases:
        result = add_staff_entry(
            session,
            name=name,
            start_time=start,
            end_time=end,
            duration=999  # Wrong value - should be auto-corrected
        )
        assert result['success'] is True
        staff = session.query(StaffTable).filter_by(name=name).first()
        assert staff.duration == expected_duration, \
            f"{name}: Expected duration {expected_duration}, got {staff.duration}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

