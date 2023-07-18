# database_operations.py

import logging
import streamlit as st
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from database.database_creation import allocations_db_tables


def connect_database():
    # Instantiate the working SQLite engine.
    engine = allocations_db_tables()[2]
    # Construct a session-maker object and bind it to the engine
    Session = sessionmaker(bind=engine)
    return Session()


def add_staff():
    staff_table = allocations_db_tables()[0]
    with connect_database() as db_session:
        name = st.text_input("Enter staff name: ", key="staff_name").title()
        role = st.text_input("Enter staff role: ",
                             key="staff_role").upper().strip() or None
        gender = st.text_input("Enter staff gender (m/f): ",
                               key="staff_gender").upper().strip()
        if st.button("Save"):
            staff = staff_table(
                name=name,
                role=role,
                gender=gender,
                assigned=False,
                start_time=0,
                end_time=12,
                duration=12
            )
            try:
                db_session.add(staff)
                db_session.commit()
                st.write(f"{name} has been added to the staff database!")
            except Exception as e:
                st.write("Error occurred while adding staff:", str(e))
                logging.error("Error occurred while adding staff:",
                              exc_info=True)


def add_patient():
    patient_table = allocations_db_tables()[1]
    with connect_database() as db_session:
        name = st.text_input("Name", key='add_patient').title()
        observation_level = st.text_input("Observation level ", key="obs_level")
        obs_type = st.text_input(
            "Observation details e.g. eyesight, arms-length, no bathroom "
            "privacy... ")
        room_number = st.text_input("Room number", key="room_number")
        gender_req = st.text_input("Staff gender required for obs m/f: ",
                                   key="gender_req", autocomplete=None).upper()
        if st.button("Save"):
            patient = patient_table(
                name=name,
                observation_level=observation_level,
                obs_type=obs_type,
                room_number=room_number,
                gender_req=gender_req
            )
            try:
                db_session.add(patient)
                db_session.commit()
                st.write(f"{name} has been added to the patient database!")
            except Exception as e:
                st.write("Error occurred while adding patient:", str(e))
                logging.error("Error occurred while adding patient:",
                              exc_info=True)


def update_staff():
    staff_table = allocations_db_tables()[0]
    patient_table = allocations_db_tables()[1]
    with connect_database() as db_session:
        staff_name = st.text_input("Enter staff name to update: ",
                                   key="staff_to_update").title()
        if staff_name:
            staff = db_session.query(staff_table).filter_by(
                name=staff_name).first()

            if staff is not None:
                staff.name = st.text_input(
                    f"Enter staff name (ignore to keep {staff.name}): ",
                    key="change_name",
                    placeholder=staff.name).title() or staff.name

                staff.role = st.text_input(
                    "Enter staff role (ignore to keep existing role): ",
                    key="change_role",
                    placeholder=staff.role) or staff.role

                staff.gender = st.text_input(
                    "Enter staff gender (ignore to keep existing gender): ",
                    key="change_gender",
                    placeholder=staff.gender).upper() or staff.gender

                if st.button("Assign / Unassigned"):
                    # Negate the current value of staff.assigned
                    staff.assigned = not staff.assigned  # Toggles boolean

                # Let user know the current assignment status
                st.write(
                    f"Assignment status: {staff.assigned}")

                # Prompt to enter the start and end times for the staff member
                start_time = st.text_input("Enter start time HH:MM: ",
                                           key="start_time")
                end_time = st.text_input("Enter end time HH:MM: ",
                                         key="end_time")

                day_converter = {'08:00': 0, '09:00': 1, '10:00': 2, '11:00': 3,
                                 '12:00': 4, '13:00': 5, '14:00': 6, '15:00': 7,
                                 '16:00': 8, '17:00': 9, '18:00': 10,
                                 '19:00': 11}
                night_converter = {'20:00': 0, '21:00': 1, '22:00': 2,
                                   '23:00': 3,
                                   '00:00': 4, '01:00': 5, '02:00': 6,
                                   '03:00': 7,
                                   '04:00': 8, '05:00': 9, '06:00': 10,
                                   '07:00': 11}
                converter = {**day_converter, **night_converter}

                day_set = set(day_converter)
                night_set = set(night_converter)

                if start_time in day_set:
                    staff.start_time = day_converter[start_time]
                    staff.start = start_time
                elif start_time in night_set:
                    staff.start_time = night_converter[start_time]
                    staff.start = start_time
                else:
                    staff.start_time = 0
                    staff.end_time = 12

                if end_time in day_set:
                    staff.end_time = day_converter[end_time]
                    staff.end = end_time
                elif end_time in night_set:
                    staff.end_time = night_converter[end_time]
                    staff.end = end_time
                else:
                    staff.start_time = 0
                    staff.end_time = 12

                staff.duration = staff.end_time - staff.start_time
                try:
                    db_session.commit()
                    st.write("Staff updated successfully.")
                except Exception as e:
                    st.write("Error occurred while updating staff:", str(e))
                    logging.error("Error occurred while updating staff:",
                                  exc_info=True)

                # Omit times logic
                ui_times = st.text_input(
                    f"Enter the hours(s) that {staff.name} should not be "
                    f"allocated to observations (ignore to keep existing "
                    f"status): ",
                    placeholder=staff.omit).split()

                if ui_times:
                    # clears the current status
                    staff.omit_time.clear()
                    staff.omit = ''

                    # st.write(converter)
                    # st.write(ui_times)

                    # converts ui times into 12-hour range for processing
                    modified_times = [converter[time] for time in ui_times if
                                      time in converter]

                    # To update both time formats in the staff table
                    time_pairs = zip(modified_times, ui_times)
                    for i, s in list(time_pairs):
                        staff.omit_time.append(i)
                        staff.omit += s + ' '

                    st.write(
                        f"{staff.omit} added to omitted times for {staff.name}.")

                # Prompt user to enter the patient name to add or remove from
                # the staff's cherry-pick list
                patient_name = st.text_input("Enter patient name to add or "
                                             "remove from staff's cherry_pick "
                                             "list (press enter to keep "
                                             "existing status): ",
                                             placeholder=staff.cherry_pick).title()

                if patient_name:
                    # Retrieve the patient from the database
                    patient = db_session.query(patient_table).filter_by(
                        name=patient_name).first()

                    # If the patient is found in the database
                    if patient:
                        # If the patient name is already in the cherry-pick
                        # list, remove it
                        if patient.name in staff.cherry_pick:
                            staff.cherry_pick.remove(patient.name)
                            st.write(f"Patient {patient.name} removed from "
                                     f"cherry-list for staff {staff.name}.")
                        else:
                            # Otherwise, add the patient name to the omit list
                            staff.cherry_pick.append(patient.name)
                            st.write(
                                f"Patient {patient.name} added to cherry-pick "
                                f"list for staff {staff.name}.")
                        db_session.commit()

                    else:
                        st.write("Patient not found.")
                if st.button("Save"):
                    db_session.commit()
                    st.write("Staff updated successfully.")
            else:
                st.write("Staff not found.")
    db_session.commit()


def editable_staff_table():
    staff_table = allocations_db_tables()[0]
    with connect_database() as db_session:
        # Construct the query to retrieve staff data from the database
        query = select(
            staff_table.name,
            staff_table.role,
            staff_table.gender,
            staff_table.assigned,
            staff_table.cherry_pick,
            staff_table.start,
            staff_table.end,
            staff_table.omit
        )

        # Execute the query and fetch the results
        result = db_session.execute(query)
        staff_data = result.fetchall()

        # Convert staff_data into a Pandas DataFrame
        column_names = ['Name', 'Role', 'Gender', 'Assigned', 'Special',
                        'Start', 'End', 'Omit']
        staff_df = pd.DataFrame(staff_data, columns=column_names)

        # This renders a data editor widget with the staff table data
        edited_staff_df = st.data_editor(data=staff_df,
                                         width=1200,
                                         height=625,
                                         column_config={
                                             'Assigned': st.column_config.CheckboxColumn()},
                                         key="staff_to_assign")

        # Update staff assignment based on the edited DataFrame
        for _, row in edited_staff_df.iterrows():
            staff_name = row['Name'].title()
            staff = db_session.query(allocations_db_tables()[0]).filter_by(
                name=staff_name).first()

            if staff.assigned != row['Assigned']:
                staff.assigned = row['Assigned']

        # Commit the changes to the database
        db_session.commit()


def editable_patient_table():
    patient_table = allocations_db_tables()[1]
    with connect_database() as db_session:
        # Construct the query to retrieve staff data from the database
        query = select(
            patient_table.name,
            patient_table.observation_level,
            patient_table.obs_type,
            patient_table.room_number,
            patient_table.gender_req,
            patient_table.omit_staff
        )

        # Execute the query and fetch the results
        result = db_session.execute(query)
        patient_data = result.fetchall()

        # Convert patient_data into a Pandas DataFrame
        column_names = ['Name', 'Obs Level', 'Obs Type', 'Room No.',
                        'Gender Reqs', 'Omit Staff']
        patient_df = pd.DataFrame(patient_data, columns=column_names)

        # This renders a data editor widget with the patient table data
        edited_patient_df = st.data_editor(data=patient_df,
                                           width=1200,
                                           height=625,
                                           hide_index=True,
                                           on_change=None,
                                           key="patient_details")

        for _, row in edited_patient_df.iterrows():
            patient_name = row[0]
            patient = db_session.query(allocations_db_tables()[1]).filter_by(
                name=patient_name).first()


def update_patient():
    staff_table = allocations_db_tables()[0]
    patient_table = allocations_db_tables()[1]
    with connect_database() as db_session:
        # Displays the patient table
        editable_patient_table()

        # Prompt user to enter the patient to update
        patient_name = st.text_input("Enter patient name to update: ",
                                     key="select_patient")
        if patient_name:
            # Retrieve the patient from the database
            patient = db_session.query(patient_table).filter_by(
                name=patient_name).first()

            # If the patient is found in the database
            if patient:
                # Update basic details
                patient.name = st.text_input(
                    f"Enter patient name (ignore to keep {patient.name}): ",
                    key="change_p_name").title() or \
                               patient.name
                patient.observation_level = st.text_input(
                    f"Enter patient obs level (ignore to keep as "
                    f"{patient.observation_level}): ",
                    key="change_obs_level") or patient.observation_level
                patient.obs_type = st.text_input(
                    f"Enter patient obs type (ignore to keep as {patient.obs_type}): ",
                    key="change_obs_type") or patient.obs_type
                patient.room_number = st.text_input(
                    f"Enter patient room number (ignore to keep as "
                    f"{patient.room_number}): ") or patient.room_number
                patient.gender_req = st.text_input(
                    "Enter any gender req m/f (press enter to clear all req): ",
                    key="change_gender").upper()

                # Omit list logic
                staff_name = st.text_input(
                    "Enter staff name to add or remove from omit_time_str list "
                    "(enter for no change): ", key="omit_list",
                    placeholder=patient.omit_staff)

                # Checks if the staff name is already in the omit list. If
                # true the db column is updated to remove it.
                if staff_name in patient.omit_staff:
                    patient.omit_staff = patient.omit_staff.remove(staff_name)
                    db_session.commit()
                    st.write(
                        f"Staff {staff_name} removed from omit list for "
                        f"patient {patient.name}.")
                else:
                    # Retrieve the staff with the given name from the database
                    staff = db_session.query(staff_table).filter_by(
                        name=staff_name).first()

                    # If the staff is found in the database
                    if staff:
                        # Add the staff id to the omit_time_str list
                        patient.omit_staff.append(staff.name)
                        st.write(f"Staff {staff.name} added to omit list for "
                                 f"patient {patient.name}.")

                        db_session.commit()  # Save the changes to the database
                    else:
                        st.write("Staff not found.")
                if st.button("Save"):
                    db_session.commit()
                    st.write("Patient updated successfully.")
            else:
                st.write("Patient not found.")


def delete_staff():
    with connect_database() as db_session:
        staff_table = allocations_db_tables()[0]
        editable_staff_table()
        staff_name = st.text_input("Enter staff name to delete: ",
                                   key="del_staff").title()
        staff = db_session.query(staff_table).filter_by(
            name=staff_name).first()
        if staff_name:
            if staff is not None:
                db_session.delete(staff)
                db_session.commit()
                st.write(f"{staff.name} has been deleted")
            else:
                st.write("Staff not found.")


def delete_patient():
    with connect_database() as db_session:
        staff_table = allocations_db_tables()[0]
        patient_table = allocations_db_tables()[1]
        editable_patient_table()
        patient_name = st.text_input("Enter patient name to delete: ",
                                     key="del_patient")
        if patient_name:
            patient = db_session.query(patient_table).filter_by(
                name=patient_name).first()

            if patient is not None:
                for staff in db_session.query(staff_table).all():
                    if patient.name in staff.cherry_pick:
                        staff.cherry_pick.remove(patient.name)
                db_session.delete(patient)
                db_session.commit()
                st.write(f"{patient_name} deleted successfully.")
            else:
                st.write("Patient not found.")


def view_staff():
    staff_table = allocations_db_tables()[0]
    with connect_database() as db_session:
        staff_list = db_session.query(staff_table).all()
        if staff_list:
            st.write("\n".join(
                [f"{staff.id} {staff.name} ({staff.role})" for staff in
                 staff_list]))
        else:
            st.write("No staff found.")


def view_patients():
    patient_table = allocations_db_tables()[1]
    with connect_database() as db_session:
        patient_list = db_session.query(patient_table).all()
        if patient_list:
            for patient in patient_list:
                omit_staff_str = ", ".join(patient.omit_staff) or "None"
                st.write(
                    f"{patient.id} {patient.name} (Observation level: "
                    f"{patient.observation_level}, Room number: "
                    f"{patient.room_number}, Gender requirement: "
                    f"{patient.gender_req}, Staff to omit_time_str: {omit_staff_str})")
        else:
            st.write("No patients found.")


if __name__ == "__main__":
    connect_database()
