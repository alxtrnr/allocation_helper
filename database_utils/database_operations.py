# database_operations.py

import os
import sys

# add the path to the custom module to the system's path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database_creation import StaffTable, ObservationsTable
from database_utils.database_viewer import display_staff, display_patients

# Create an engine to carry on with the table. This is the SQLite engine.
engine = create_engine('sqlite:///example02.db')

# Construct a sessionmaker object and bind it to the engine
Session = sessionmaker(bind=engine)
session = Session()


def add_staff():
    name = st.text_input("Enter staff name: ").title()
    role = st.text_input("Enter staff role: ").upper().strip() or None
    gender = st.text_input("Enter staff gender (m/f): ").upper().strip()
    if name and role and gender:
        staff = StaffTable(
            name=name,
            role=role,
            gender=gender,
            assigned=False,
            start_time=0,
            end_time=12,
            duration=12
        )
        session.add(staff)
        session.commit()
        st.write(f"{name} has been added to the staff database!")


def add_patient():
    name = st.text_input("Name").title()
    observation_level = st.text_input("Observation level ")
    room_number = st.text_input("Room number")
    gender_req = st.text_input("Staff gender required for obs m/f: ", autocomplete=None).upper()
    if name and observation_level and room_number and gender_req:
        patient = ObservationsTable(
            name=name,
            observation_level=observation_level,
            room_number=room_number,
            gender_req=gender_req
        )
        session.add(patient)
        session.commit()
        st.write(f"{name} has been added to the patient database!")


def update_staff():
    display_staff()
    staff_name = st.text_input("Enter staff name to update: ").title()
    staff = session.query(StaffTable).filter_by(name=staff_name).first()

    if staff is not None:
        staff.name = st.text_input(f"Enter staff name (ignore to keep {staff.name}): ",
                                   placeholder=staff.name).title() or staff.name
        staff.role = st.text_input("Enter staff role (ignore to keep existing role): ",
                                   placeholder=staff.role) or staff.role
        staff.gender = st.text_input(
            "Enter staff gender (ignore to keep existing gender): ",
            placeholder=staff.gender).upper() or staff.gender

        if st.button("Toggle Assignment Status"):
            # Negate the current value of staff.assigned
            staff.assigned = not staff.assigned  # Toggles boolean

            # Print updated status message to console
            status = "assigned" if staff.assigned else "unassigned"
            print(f"Staff member is now {status}")

        # Let user know the current assignment status
        st.write(f"Current assignment status: {'assigned' if staff.assigned else 'unassigned'}")

        start_time = st.text_input("Enter staff start time (HH:MM) (press enter if LD or N shift): ")
        end_time = st.text_input("Enter staff end time (HH:MM) (press enter if LD or N shift): ")

        day_converter = {'08:00': 0,
                         '09:00': 1,
                         '10:00': 2,
                         '11:00': 3,
                         '12:00': 4,
                         '13:00': 5,
                         '14:00': 6,
                         '15:00': 7,
                         '16:00': 8,
                         '17:00': 9,
                         '18:00': 10,
                         '19:00': 11
                         }
        night_converter = {'20:00': 0,
                           '21:00': 1,
                           '22:00': 2,
                           '23:00': 3,
                           '00:00': 4,
                           '01:00': 5,
                           '02:00': 6,
                           '03:00': 7,
                           '04:00': 8,
                           '05:00': 9,
                           '06:00': 10,
                           '07:00': 11
                           }
        if start_time in day_converter.keys():
            staff.start_time = day_converter[start_time]
            staff.end_time = day_converter[end_time]
        elif start_time in night_converter.keys():
            staff.start_time = night_converter[start_time]
            staff.end_time = night_converter[end_time]
        else:
            staff.start_time = 0
            staff.end_time = 12
        staff.duration = staff.end_time - staff.start_time

        # Prompt user to enter the times to add or remove from an exclude times list which will then be created
        times = st.text_input(
            f"Enter the time(s) you want to add or remove from omit_time (ignore to keep existing status): ",
            placeholder=f"Time {staff.omit_time} are omitted.").split() or []

        # If times are provided
        if len(times) > 0:
            for omit_time in times:
                staff.omit_time.append(int(omit_time))
                st.write(f"Time {omit_time} added to omit time list for staff {staff.name}.")
        else:
            staff.omit_time = []
        session.commit()  # Save the changes to the database

        # Prompt user to enter the patient ID to add or remove from the staff's cherry-pick list
        patient_name = st.text_input(
            "Enter patient name to add or remove from staff's cherry_pick list (press enter to keep existing status): ",
            placeholder=staff.cherry_pick).title()
        # If the patient ID is provided
        if patient_name:
            # Retrieve the patient with the given ID from the database
            patient = session.query(ObservationsTable).filter_by(name=patient_name).first()

            # If the patient is found in the database
            if patient:
                # If the patient name is already in the cherry-pick list, remove it
                if patient.name in staff.cherry_pick:
                    staff.cherry_pick.remove(patient.name)
                    st.write(f"Patient {patient.name} removed from cherry-list for staff {staff.name}.")
                else:
                    # Otherwise, add the patient name to the omit list
                    staff.cherry_pick.append(patient.name)
                    st.write(f"Patient {patient.name} added to cherry-pick list for staff {staff.name}.")

                session.commit()  # Save the changes to the database
            else:
                st.write("Patient not found.")
        session.commit()
        st.write("Staff updated successfully.")
    else:
        st.write("Staff not found.")


def update_patient():
    display_patients()
    # Prompt user to enter the patient ID to update
    patient_name = st.text_input("Enter patient name to update: ")

    # Retrieve the patient with the given ID from the database
    patient = session.query(ObservationsTable).filter_by(name=patient_name).first()

    # If the patient is found in the database
    if patient:
        # Prompt user to enter the patient name, observation level, and room number
        patient.name = st.text_input(
            f"Enter patient name (ignore to keep as {patient.name}): ").title() or patient.name
        patient.observation_level = st.text_input(
            f"Enter patient obs level (ignore to keep as {patient.observation_level}): ") or patient.observation_level
        patient.room_number = st.text_input(
            f"Enter patient room number (ignore to keep as {patient.room_number}): ") or patient.room_number
        patient.gender_req = st.text_input(
            "Enter any gender req m/f (press enter to clear all req): ").upper()
        # Prompt user to enter the staff ID to add or remove from the patient's omit list
        staff_id = st.text_input("Enter staff ID to add or remove from omit list (press enter to keep existing "
                                 "status): ")

        # If the staff ID is provided
        if staff_id:
            # Retrieve the staff with the given ID from the database
            staff = session.query(StaffTable).filter_by(id=staff_id).first()

            # If the staff is found in the database
            if staff:
                # If the staff name is already in the omit list, remove it
                if staff.name in patient.omit_staff:
                    patient.omit_staff.remove(staff.name)
                    st.write(f"Staff {staff.name} removed from omit list for patient {patient.name}.")
                else:
                    # Otherwise, add the staff name to the omit list
                    patient.omit_staff.append(staff.name)
                    st.write(f"Staff {staff.name} added to omit list for patient {patient.name}.")

                session.commit()  # Save the changes to the database
            else:
                st.write("Staff not found.")
        else:
            session.commit()  # Save the changes to the database
            st.write("Patient updated successfully.")
    else:
        st.write("Patient not found.")


def delete_staff():
    display_staff()
    staff_name = st.text_input("Enter staff name to delete: ")
    staff = session.query(StaffTable).filter_by(name=staff_name).first()

    if staff is not None:
        st.write(f"{staff.name} has been deleted...")
        session.delete(staff)
        st.write("...successfully.")
        session.commit()

    else:
        st.write("Staff not found.")


def delete_patient():
    display_patients()
    patient_name = st.text_input("Enter patient name to delete: ")
    patient = session.query(ObservationsTable).filter_by(name=patient_name).first()

    if patient is not None:
        # Remove the patient name from the cherry-pick list of all staff members
        for staff in session.query(StaffTable).all():
            if patient.name in staff.cherry_pick:
                staff.cherry_pick.remove(patient.name)
        session.delete(patient)
        session.commit()
        st.write("Patient deleted successfully.")
    else:
        st.write("Patient not found.")


def view_staff():
    staff_list = session.query(StaffTable).all()
    if staff_list:
        st.write("\n".join([f"{staff.id} {staff.name} ({staff.role})" for staff in staff_list]))
    else:
        st.write("No staff found.")


def view_patients():
    patient_list = session.query(ObservationsTable).all()
    if patient_list:
        for patient in patient_list:
            omit_staff_str = ", ".join(patient.omit_staff) or "None"
            st.write(
                f"{patient.id} {patient.name} (Observation level: {patient.observation_level}, Room number: {patient.room_number}, Gender requirement: {patient.gender_req}, Staff to omit: {omit_staff_str})")
    else:
        st.write("No patients found.")
