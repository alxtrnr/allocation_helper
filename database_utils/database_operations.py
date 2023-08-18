# database_operations.py

import logging
import streamlit as st
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from database.database_creation import allocations_db_tables

STAFF_DB, PATIENT_DB, ENGINE = allocations_db_tables()


# ---- Database Operations ----

def connect_database():
    Session = sessionmaker(bind=ENGINE)
    return Session()


def handle_database_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error occurred:", exc_info=True)
            st.write(f"An error occurred: {str(e)}")

    return wrapper


@handle_database_exception
def add_data_to_database(db_session, data):
    db_session.add(data)
    db_session.commit()


@handle_database_exception
def delete_data_from_database(db_session, data):
    db_session.delete(data)
    db_session.commit()


# ---- User Interface Functions ----

def add_staff():
    st.markdown("#### :blue[Add Staff]")
    with connect_database() as db_session:
        name = st.text_input("staff_name", key="staff_name",
                             label_visibility='hidden',
                             placeholder='Name').title()

        if st.button(":blue[**Add Staff**]"):
            staff = STAFF_DB(
                name=name,
                role='HCA',
                gender='F',
                assigned=False,
                start_time=0,
                end_time=12,
                duration=12
            )

            add_data_to_database(db_session, staff)
            st.write(f"{name} has been added to the staff database!")
            st.experimental_rerun()


def add_patient():
    st.markdown("#### :blue[Add Patient]")
    with connect_database() as db_session:
        name = st.text_input("patient_name", key='patient_name',
                             label_visibility="hidden",
                             placeholder="Name").title()

        if st.button(":blue[**Add Patient**]"):
            patient = PATIENT_DB(
                name=name,
                observation_level=0,
                obs_type=None,
                room_number=None,
                gender_req=None
            )
            add_data_to_database(db_session, patient)
            st.write(f"{name} has been added to the patient database!")
            st.experimental_rerun()


def delete_staff():
    st.markdown("#### :red[Delete Staff]")
    with connect_database() as db_session:
        slist = [s.name for s in db_session.query(STAFF_DB)]
        staff_selector = st.selectbox('**:red[Delete]**',
                                      options=slist, index=0,
                                      key="delete_staff_selector", help=None,
                                      on_change=None, args=None, kwargs=None,
                                      placeholder="Select...", disabled=False,
                                      label_visibility="hidden")

        if st.button("**:red[Delete Staff]**"):
            for staff in db_session.query(STAFF_DB):
                if staff.name == staff_selector:
                    delete_data_from_database(db_session, staff)
                    st.experimental_rerun()


def delete_patient():
    st.markdown("#### :red[Delete Patient]")
    with connect_database() as db_session:
        p_list = [p.name for p in db_session.query(PATIENT_DB)]
        patient_selector = st.selectbox('**:red[Delete]**',
                                        options=p_list, index=0,
                                        key="delete_staff_selector", help=None,
                                        on_change=None, args=None, kwargs=None,
                                        placeholder="Select...", disabled=False,
                                        label_visibility="hidden")

        if st.button("**:red[Delete Patient]**"):
            for patient in db_session.query(PATIENT_DB):
                if patient.name == patient_selector:
                    for staff in db_session.query(STAFF_DB).all():
                        if patient.name in staff.special_list:
                            staff.special_list.remove(patient.name)
                    delete_data_from_database(db_session, patient)
                    st.experimental_rerun()


def view_staff():
    with connect_database() as db_session:
        staff_list = db_session.query(STAFF_DB).all()
        if staff_list:
            st.write("\n".join(
                [f"{staff.id} {staff.name} ({staff.role})" for staff in
                 staff_list]))
        else:
            st.write("No staff found.")


def view_patients():
    with connect_database() as db_session:
        patient_list = db_session.query(PATIENT_DB).all()
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


def staff_data_editor():
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
    hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
             '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
             '20:00', '21:00', '22:00', '23:00', '00:00', '01:00',
             '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'
             ]

    patient_table = allocations_db_tables()[1]

    with connect_database() as db_session:
        # Construct the query to retrieve staff data from the database
        query = select(
            STAFF_DB.name,
            STAFF_DB.role,
            STAFF_DB.gender,
            STAFF_DB.assigned,
            STAFF_DB.special_string,
            STAFF_DB.special_list,
            STAFF_DB.start,
            STAFF_DB.end,
            STAFF_DB.omit
        )

        patients_names = select(PATIENT_DB.name)

        # Execute the query and fetch the results
        result = db_session.execute(query)
        staff_data = result.all()

        p_names = db_session.execute(patients_names)
        patients = [name[0] for name in p_names.all()]

        # Convert staff_data into a Pandas DataFrame
        column_names = ['Name', 'Role', 'Gender', 'Assign', 'String',
                        'Cherry Pick', 'Start', 'End', 'Omit']
        staff_df = pd.DataFrame(staff_data, columns=column_names)

        # This renders a data editor widget with the staff table data
        edited_staff_df = st.data_editor(data=staff_df,
                                         width=1200,
                                         height=625,
                                         hide_index=True,
                                         column_config={
                                             'Name': st.column_config.TextColumn(
                                                 label=None, width="small",
                                                 help="Enter staff name",
                                                 disabled=None, required=None,
                                                 default="Name", max_chars=None,
                                                 validate=None),

                                             'Role': st.column_config.SelectboxColumn(
                                                 label='Role', width="small",
                                                 help="Select role from the "
                                                      "dropdown box",
                                                 disabled=None, required=None,
                                                 default=None,
                                                 options=['HCA', 'RMN']),

                                             'Gender': st.column_config.SelectboxColumn(
                                                 label=None, width="small",
                                                 help="Select gender from the"
                                                      "dropdown box",
                                                 disabled=None, required=None,
                                                 default=None,
                                                 options=['M', 'F']),

                                             'Assign': st.column_config.CheckboxColumn(
                                                 label='Allocations',
                                                 width="small",
                                                 help='Assign staff on/off to '
                                                      'observations',
                                                 disabled=None,
                                                 required=None, default=None
                                             ),

                                             'String': st.column_config.SelectboxColumn(
                                                 label="Selector",
                                                 width="small",
                                                 help='Select from the drop '
                                                      'down box to add/remove '
                                                      'patient(s) cherry picked'
                                                      ' for this staff.',
                                                 disabled=None,
                                                 required=None, default=None,
                                                 options=patients),

                                             'Cherry Pick': st.column_config.TextColumn(
                                                 label=None, width="small",
                                                 help='Only assign to obs for '
                                                      'the names shown',
                                                 disabled=True,
                                                 required=None, default=None),

                                             'Start': st.column_config.SelectboxColumn(
                                                 label="Start Time",
                                                 width="small",
                                                 help="Start time is the normal"
                                                      " time for d/n shift "
                                                      "unless a custom time is "
                                                      "specified below.",
                                                 disabled=None, required=None,
                                                 default=None, options=hours),

                                             'End': st.column_config.SelectboxColumn(
                                                 label="End Time",
                                                 width="small",
                                                 help="End time is the normal"
                                                      " time for d/n shift "
                                                      "unless a custom time is "
                                                      "specified below.",
                                                 disabled=None,
                                                 required=None, default=None,
                                                 options=hours),

                                             'Omit': st.column_config.TextColumn(
                                                 label=None, width="small",
                                                 help='HH:00 separated by a '
                                                      'space for any time when '
                                                      'observations should not '
                                                      'be assigned',
                                                 disabled=None,
                                                 required=None, default=None,
                                                 max_chars=None,
                                                 # hh:mm or hh:mm hh:mm...
                                                 validate="^(?:([01][0-9]|2[0-3]):00(?:\s|$))+"),
                                         },
                                         key="staff_df"
                                         )

        df_names = [row['Name'].title() for _, row in
                    edited_staff_df.iterrows()]
        df_role = [row['Role'].upper() for _, row in
                   edited_staff_df.iterrows()]
        df_gender = [row['Gender'].upper() for _, row in
                     edited_staff_df.iterrows()]
        df_assign = [row['Assign'] for _, row in
                     edited_staff_df.iterrows()]
        df_start = [row['Start'].title() for _, row in
                    edited_staff_df.iterrows()]
        df_end = [row['End'].title() for _, row in
                  edited_staff_df.iterrows()]
        df_omit = [row['Omit'] for _, row in
                   edited_staff_df.iterrows()]
        df_special = [row['String'] for _, row in
                      edited_staff_df.iterrows()]

        # The following conditional statements check and sync entries between
        # the editable dataframe and database

        # names
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_names):
            if db_entry.name != df_entry:
                db_entry.name = df_entry
                db_session.commit()
                st.experimental_rerun()

        # role
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_role):
            if db_entry.role != df_entry:
                db_entry.role = df_entry
                db_session.commit()
                st.experimental_rerun()

        # gender
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_gender):
            if db_entry.gender != df_entry:
                db_entry.gender = df_entry
                db_session.commit()
                st.experimental_rerun()

        # select / deselect for allocation
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_assign):
            if db_entry.assigned != df_entry:
                db_entry.assigned = df_entry
                db_session.commit()
                st.experimental_rerun()

        # start time
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_start):
            if db_entry.start != df_entry:
                db_entry.start = df_entry
                if df_entry in day_set:
                    db_entry.start_time = day_converter[df_entry]
                elif df_entry in night_set:
                    db_entry.start_time = night_converter[df_entry]
                else:
                    db_entry.start_time = 0
                db_session.commit()
                st.experimental_rerun()

        # end time
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_end):
            if db_entry.end != df_entry:
                db_entry.end = df_entry
                if df_entry in day_set:
                    db_entry.end_time = day_converter[df_entry]
                elif df_entry in night_set:
                    db_entry.end_time = night_converter[df_entry]
                else:
                    db_entry.end_time = 12
                db_session.commit()
                st.experimental_rerun()

        # omit times
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_omit):
            if db_entry.omit != df_entry:
                db_entry.omit = df_entry
                db_entry.omit_time.clear()
                df_entry_list = df_entry.split()

                # converts times entered into the dataframe to the 12-hour
                # range for processing
                modified_times = [converter[time] for time in df_entry_list if
                                  time in converter]

                # updates the database list of times (12 hour range) to be
                # omitted
                for twelve_hour_range in modified_times:
                    db_entry.omit_time.append(twelve_hour_range)
                    db_session.commit()
                    st.experimental_rerun()

        # cherry-pick
        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[0]), df_special):
            if df_entry:
                if df_entry not in db_entry.special_list:
                    db_entry.special_list.append(df_entry)
                elif df_entry in db_entry.special_list:
                    db_entry.special_list.pop(
                        db_entry.special_list.index(df_entry))
                db_session.commit()
                st.experimental_rerun()

    col1, col2 = st.columns(2)
    with col1:
        add_staff()
    with col2:
        delete_staff()


def patient_data_editor():
    with connect_database() as db_session:
        # Construct query to retrieve patient data from the database
        query = select(
            PATIENT_DB.name,
            PATIENT_DB.observation_level,
            PATIENT_DB.obs_type,
            PATIENT_DB.room_number,
            PATIENT_DB.gender_req,
            PATIENT_DB.omit_staff_selector,
            PATIENT_DB.omit_staff
        )
        result = db_session.execute(query)
        patient_data = result.fetchall()

        # Construct query to retrieve staff data from the database
        staff_names = select(STAFF_DB.name)
        s_names = db_session.execute(staff_names)
        staff = [name[0] for name in s_names.all()]

        # Convert patient_data into a Pandas DataFrame
        column_names = ['Name', 'Obs Level', 'Obs Type', 'Room No',
                        'Gender Reqs', 'Selector', 'Omit Staff']
        patient_df = pd.DataFrame(patient_data, columns=column_names)

        # This renders a data editor widget with the patient table data
        edited_patient_df = st.data_editor(data=patient_df,
                                           width=1200,
                                           height=625,
                                           hide_index=True,
                                           column_config={
                                               'Name': st.column_config.TextColumn(
                                                   label=None, width="small",
                                                   help="Enter the patient's "
                                                        "name",
                                                   disabled=None,
                                                   required=None,
                                                   default="Name",
                                                   max_chars=None,
                                                   validate=None),

                                               'Obs Level': st.column_config.SelectboxColumn(
                                                   label=None, width="small",
                                                   help="Select the obs level "
                                                        "0 = Generals, 1 = 1:1,"
                                                        " 2 = 2:1 and so on...",
                                                   disabled=None,
                                                   required=None, default=0,
                                                   options=[0, 1, 2, 3, 4]),

                                               'Obs Type': st.column_config.TextColumn(
                                                   label=None, width="large",
                                                   help='Any details e.g. '
                                                        'arms-length, eyesight '
                                                        'or bathroom privacy',
                                                   disabled=None, required=None,
                                                   default=None, max_chars=None,
                                                   validate=None),

                                               'Room No': st.column_config.SelectboxColumn(
                                                   label=None, width="small",
                                                   help="Select the room "
                                                        "number.",
                                                   disabled=None,
                                                   required=None, default=None,
                                                   options=['01', '02', '03',
                                                            '04', '05', '06',
                                                            '07', '08', '09',
                                                            '10', '11', '12',
                                                            '13', '14', '15',
                                                            '16']),

                                               'Gender Reqs': st.column_config.SelectboxColumn(
                                                   label=None, width="small",
                                                   help="If specified only"
                                                        " male or female staff "
                                                        "will be assigned to "
                                                        "the patients obs.",
                                                   disabled=None,
                                                   required=None,
                                                   default=None,
                                                   options=["F", "M"]),

                                               'Selector': st.column_config.SelectboxColumn(
                                                   label="Selector",
                                                   width="small",
                                                   help='Select from the drop '
                                                        'down box to exclude '
                                                        'staff from this '
                                                        'patients observations.',
                                                   disabled=None,
                                                   required=None, default=None,
                                                   options=staff),

                                               'Omit Staff': st.column_config.TextColumn(
                                                   label="Excluded from obs",
                                                   width="small",
                                                   help="Named staff will not "
                                                        "be allocated to "
                                                        "observations for "
                                                        "this patient",
                                                   disabled=True, required=None,
                                                   default="Name",
                                                   max_chars=None,
                                                   validate=None),
                                           },
                                           key="patient_df"
                                           )

        df_names = [row['Name'] for _, row in edited_patient_df.iterrows()]
        df_obs_level = [row['Obs Level'] for _, row in
                        edited_patient_df.iterrows()]
        df_obs_type = [row['Obs Type'] for _, row in
                       edited_patient_df.iterrows()]
        df_room_no = [row['Room No'] for _, row in
                      edited_patient_df.iterrows()]
        df_gender_req = [row['Gender Reqs'] for _, row in
                         edited_patient_df.iterrows()]
        df_selector = [row['Selector'] for _, row in
                       edited_patient_df.iterrows()]

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_names):
            if db_entry.name != df_entry:
                db_entry.name = df_entry

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_obs_level):
            if db_entry.observation_level != df_entry:
                db_entry.observation_level = df_entry

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_obs_type):
            if db_entry.obs_type != df_entry:
                db_entry.obs_type = df_entry

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_room_no):
            if db_entry.room_number != df_entry:
                db_entry.room_number = df_entry

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_gender_req):
            if db_entry.gender_req != df_entry:
                db_entry.gender_req = df_entry

        for db_entry, df_entry in zip(
                db_session.query(allocations_db_tables()[1]), df_selector):
            if df_entry:
                if df_entry not in db_entry.omit_staff:
                    db_entry.omit_staff.append(df_entry)
                elif df_entry in db_entry.omit_staff:
                    db_entry.omit_staff.pop(
                        db_entry.omit_staff.index(df_entry))

        db_session.commit()

    col1, col2 = st.columns(2)
    with col1:
        add_patient()
    with col2:
        delete_patient()


# ---- Main Function ----

def main():
    st.title("Database Operations")

    operation = st.sidebar.selectbox("Select Operation",
                                     ["Add Staff", "Add Patient",
                                      "Delete Staff", "Delete Patient"])

    if operation == "Add Staff":
        add_staff()
    elif operation == "Add Patient":
        add_patient()
    elif operation == "Delete Staff":
        delete_staff()
    elif operation == "Delete Patient":
        delete_patient()

    st.sidebar.subheader("View Data")
    if st.sidebar.button("View Staff"):
        view_staff()
    if st.sidebar.button("View Patients"):
        view_patients()


if __name__ == "__main__":
    main()
