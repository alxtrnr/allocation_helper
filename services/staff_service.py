from sqlalchemy.exc import SQLAlchemyError
from models import StaffTable

VALID_ROLES = ['HCA', 'RMN']
VALID_GENDERS = ['F', 'M']

def add_staff_entry(db_session, name, role='HCA', gender='F', assigned=False, start_time=0, end_time=12, duration=12):
    name = (name or '').strip().title()
    if not name:
        return {'success': False, 'message': 'Staff name cannot be empty.'}
    if role not in VALID_ROLES:
        return {'success': False, 'message': f'Role must be one of: {VALID_ROLES}'}
    if gender not in VALID_GENDERS:
        return {'success': False, 'message': f'Gender must be one of: {VALID_GENDERS}'}
    
    # Validate time range
    if start_time < 0 or start_time > 12:
        return {'success': False, 'message': 'Start time must be between 0 and 12.'}
    if end_time < 0 or end_time > 12:
        return {'success': False, 'message': 'End time must be between 0 and 12.'}
    if start_time >= end_time:
        return {'success': False, 'message': 'End time must be greater than start time.'}
    
    # Auto-correct duration to match actual working hours
    actual_hours = end_time - start_time
    if duration != actual_hours:
        duration = actual_hours  # Auto-correct
    
    existing = db_session.query(StaffTable).filter_by(name=name).first()
    if existing:
        return {'success': False, 'message': f'A staff member with name "{name}" already exists.'}
    try:
        staff = StaffTable(
            name=name,
            role=role,
            gender=gender,
            assigned=assigned,
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )
        db_session.add(staff)
        db_session.commit()
        return {'success': True, 'object': staff, 'message': f'Staff {name} added.'}
    except SQLAlchemyError as e:
        db_session.rollback()
        return {'success': False, 'message': f'Database error: {str(e)}'}

def update_staff_entry(db_session, staff_id, name=None, role=None, gender=None, assigned=None, start_time=None, end_time=None, duration=None):
    staff = db_session.query(StaffTable).get(staff_id)
    if not staff:
        return {'success': False, 'message': f'Staff with id {staff_id} not found.'}
    if name is not None:
        normalized_name = (name or '').strip().title()
        if not normalized_name:
            return {'success': False, 'message': 'Staff name cannot be empty.'}
        # Check for duplicate name (don't count self):
        existing = db_session.query(StaffTable).filter(StaffTable.name == normalized_name, StaffTable.id != staff_id).first()
        if existing:
            return {'success': False, 'message': f'Another staff member with name "{normalized_name}" already exists.'}
        staff.name = normalized_name
    if role is not None:
        if role not in VALID_ROLES:
            return {'success': False, 'message': f'Role must be one of: {VALID_ROLES}'}
        staff.role = role
    if gender is not None:
        if gender not in VALID_GENDERS:
            return {'success': False, 'message': f'Gender must be one of: {VALID_GENDERS}'}
        staff.gender = gender
    if assigned is not None:
        staff.assigned = assigned
    if start_time is not None:
        if start_time < 0 or start_time > 12:
            return {'success': False, 'message': 'Start time must be between 0 and 12.'}
        staff.start_time = start_time
    if end_time is not None:
        if end_time < 0 or end_time > 12:
            return {'success': False, 'message': 'End time must be between 0 and 12.'}
        staff.end_time = end_time
    
    # Validate time range consistency
    if staff.start_time >= staff.end_time:
        return {'success': False, 'message': 'End time must be greater than start time.'}
    
    # Auto-correct duration to match actual working hours
    actual_hours = staff.end_time - staff.start_time
    if duration is not None:
        if duration != actual_hours:
            duration = actual_hours  # Auto-correct
    else:
        # Even if duration wasn't explicitly provided, ensure it's correct
        if staff.duration != actual_hours:
            duration = actual_hours
    
    if duration is not None:
        staff.duration = duration
    
    try:
        db_session.commit()
        return {'success': True, 'object': staff, 'message': f'Staff {staff.name} updated.'}
    except SQLAlchemyError as e:
        db_session.rollback()
        return {'success': False, 'message': f'Database error: {str(e)}'}

def delete_staff_entry(db_session, staff_name):
    staff_to_delete = db_session.query(StaffTable).filter_by(name=staff_name).first()
    if staff_to_delete:
        db_session.delete(staff_to_delete)
        db_session.commit()
        return True
    return False

def check_allocation_feasibility(db_session):
    from models import PatientTable
    staff_list = db_session.query(StaffTable).filter_by(assigned=True).all()
    patient_list = db_session.query(PatientTable).all()
    # Count for each obs slot/time, what's minimally required.
    min_staff_per_time = [0] * 12  # Assume 12 slots/blocks per day
    for p in patient_list:
        try:
            level = int(p.observation_level or 0)
        except (ValueError, TypeError):
            level = 0
        if level > 0:
            for t in range(12):
                min_staff_per_time[t] += level
    # For each time slot, count available staff
    available_per_time = [0] * 12
    for s in staff_list:
        for t in range(12):
            if s.start_time <= t < s.end_time:
                available_per_time[t] += 1
    # Warnings, errors
    warnings = []
    for t, (req, av) in enumerate(zip(min_staff_per_time, available_per_time)):
        if av < req:
            warnings.append(f"Hour {t}: Need {req}, available {av} (shortfall: {req-av})")
    if warnings:
        return {
            'success': False,
            'message': 'Infeasible: Not enough staff to cover all required observations for at least one hour.',
            'warnings': warnings
        }
    return {'success': True, 'message': 'Coverage is feasible for all hours.', 'warnings': []}
