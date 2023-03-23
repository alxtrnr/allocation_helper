# milo_input_data.py

from database.database_creation import StaffTable, ObservationsTable, engine, Base, sessionmaker

# Create a session factory
Session = sessionmaker(bind=engine)

# Create the tables if they don't exist
Base.metadata.create_all(engine)


def get_staff_rows_as_dict():
    # Create a session object
    session = Session()
    # Query the StaffTable and return the dictionaries of each row
    staff_rows = session.query(StaffTable).all()
    staff_rows_as_dict = [staff_row.as_dict() for staff_row in staff_rows]
    # Close the session
    session.close()
    return staff_rows_as_dict


def get_patient_rows_as_dict():
    # Create a session object
    session = Session()
    # Query the ObservationsTable and return the dictionaries of each row
    patient_rows = session.query(ObservationsTable).all()
    patient_rows_as_dict = [patient_row.as_dict() for patient_row in patient_rows]
    # Close the session
    session.close()
    return patient_rows_as_dict


# Print the dictionaries of each row in the StaffTable
# staff_rows_as_dict = get_staff_rows_as_dict()
# print('\nStaff')
# for staff_row in staff_rows_as_dict:
#     print(staff_row)

# Print the dictionaries of each row in the ObservationsTable
# patient_rows_as_dict = get_patient_rows_as_dict()
# print('\nObservations')
# for patient_row in patient_rows_as_dict:
#     print(patient_row)

