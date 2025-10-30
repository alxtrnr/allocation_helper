from sqlalchemy.exc import SQLAlchemyError
from models import PatientTable, StaffTable

def add_patient_entry(db_session, name, observation_level=0, obs_type=None, room_number=None, gender_req=None):
    name = (name or '').strip().title()
    if not name:
        return {'success': False, 'message': 'Patient name cannot be empty.'}
    existing = db_session.query(PatientTable).filter_by(name=name).first()
    if existing:
        return {'success': False, 'message': f'A patient with name "{name}" already exists.'}
    try:
        patient = PatientTable(
            name=name,
            observation_level=observation_level,
            obs_type=obs_type,
            room_number=room_number,
            gender_req=gender_req
        )
        db_session.add(patient)
        db_session.commit()
        return {'success': True, 'object': patient, 'message': f'Patient {name} added.'}
    except SQLAlchemyError as e:
        db_session.rollback()
        return {'success': False, 'message': f'Database error: {str(e)}'}

def update_patient_entry(db_session, patient_id, name=None, observation_level=None, obs_type=None, room_number=None, gender_req=None):
    patient = db_session.query(PatientTable).get(patient_id)
    if not patient:
        return {'success': False, 'message': f'Patient with id {patient_id} not found.'}
    if name is not None:
        normalized_name = (name or '').strip().title()
        if not normalized_name:
            return {'success': False, 'message': 'Patient name cannot be empty.'}
        existing = db_session.query(PatientTable).filter(PatientTable.name == normalized_name, PatientTable.id != patient_id).first()
        if existing:
            return {'success': False, 'message': f'Another patient with name "{normalized_name}" already exists.'}
        patient.name = normalized_name
    if observation_level is not None:
        patient.observation_level = observation_level
    if obs_type is not None:
        patient.obs_type = obs_type
    if room_number is not None:
        patient.room_number = room_number
    if gender_req is not None:
        patient.gender_req = gender_req
    try:
        db_session.commit()
        return {'success': True, 'object': patient, 'message': f'Patient {patient.name} updated.'}
    except SQLAlchemyError as e:
        db_session.rollback()
        return {'success': False, 'message': f'Database error: {str(e)}'}

def delete_patient_entry(db_session, patient_name):
    patient_to_delete = db_session.query(PatientTable).filter_by(name=patient_name).first()
    if patient_to_delete:
        # Remove from special_list in all staff
        for staff in db_session.query(StaffTable).all():
            if patient_name in staff.special_list:
                staff.special_list.remove(patient_name)
        db_session.delete(patient_to_delete)
        db_session.commit()
        return True
    return False
