# milo_input_data.py

from database.database_creation import allocations_db_tables
from sqlalchemy.orm import sessionmaker


def connect_database():
    # Instantiate the working SQLite engine.
    engine = allocations_db_tables()[2]

    # Construct a session-maker object and bind it to the engine
    Session = sessionmaker(bind=engine)

    return Session()


def get_staff_rows_as_dict():
    staff_table = allocations_db_tables()[0]
    with connect_database() as session:
        staff_rows = session.query(staff_table).all()
        staff_rows_as_dict = [staff_row.as_dict() for staff_row in staff_rows]

    return staff_rows_as_dict


def get_patient_rows_as_dict():
    patient_table = allocations_db_tables()[1]
    with connect_database() as session:
        patient_rows = session.query(patient_table).all()
        patient_rows_as_dict = [patient_row.as_dict() for patient_row in
                                patient_rows]

    return patient_rows_as_dict

# Print the dictionaries of each row in the StaffTable
# staff_rows_as_dict = get_staff_rows_as_dict()
# print('\nStaff')
# for staff_row in staff_rows_as_dict:
#     print(staff_row)

# Print the dictionaries of each row in the PatientTable
# patient_rows_as_dict = get_patient_rows_as_dict()
# print('\nObservations')
# for patient_row in patient_rows_as_dict:
#     print(patient_row)


if __name__ == "__main__":
    connect_database()
