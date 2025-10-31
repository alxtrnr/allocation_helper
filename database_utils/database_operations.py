# database_operations.py

import logging
import streamlit as st
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from database.database_creation import allocations_db_tables
from utils.time_utils import TIME_CONVERTER, CONVERTER_DAY, CONVERTER_NIGHT, hour_str_to_index, times_list_to_indices, ALL_HOURS
from services.staff_service import add_staff_entry
from services.patient_service import add_patient_entry
from services.staff_service import delete_staff_entry
from services.patient_service import delete_patient_entry
from services.staff_service import update_staff_entry
from services.patient_service import update_patient_entry

# Helper accessors to avoid module-level initialization

def get_staff_db():
    return allocations_db_tables()[0]

def get_patient_db():
    return allocations_db_tables()[1]

def get_engine():
    return allocations_db_tables()[2]


# ---- Database Operations ----

def connect_database():
    Session = sessionmaker(bind=get_engine())
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
    db_session = connect_database()
    try:
        name = st.text_input("staff_name", key="staff_name",
                             label_visibility='hidden',
                             placeholder='Name').title()
        # Optional: add UI fields for selecting role/gender
        role = 'HCA'
        gender = 'F'
        # TODO: Could add selectable fields here like role = st.radio, etc.
        if st.button(":blue[**Add Staff**]"):
            result = add_staff_entry(db_session, name=name, role=role, gender=gender)
            if result['success']:
                st.write(result['message'])
                st.experimental_rerun()
            else:
                st.error(result['message'])
    finally:
        db_session.close()


def add_patient():
    st.markdown("#### :blue[Add Patient]")
    db_session = connect_database()
    try:
        name = st.text_input("patient_name", key='patient_name',
                             label_visibility="hidden",
                             placeholder="Name").title()
        if st.button(":blue[**Add Patient**]"):
            result = add_patient_entry(db_session, name=name)
            if result['success']:
                st.write(result['message'])
                st.experimental_rerun()
            else:
                st.error(result['message'])
    finally:
        db_session.close()


def delete_staff():
    st.markdown("#### :red[Delete Staff]")
    db_session = connect_database()
    try:
        slist = [s.name for s in db_session.query(get_staff_db())]
        staff_selector = st.selectbox('**:red[Delete]**',
                                      options=slist, index=0,
                                      key="delete_staff_selector", help=None,
                                      on_change=None, args=None, kwargs=None,
                                      placeholder="Select...", disabled=False,
                                      label_visibility="hidden")

        if st.button("**:red[Delete Staff]**"):
            delete_staff_entry(db_session, staff_selector)
            st.experimental_rerun()
    finally:
        db_session.close()


def delete_patient():
    st.markdown("#### :red[Delete Patient]")
    db_session = connect_database()
    try:
        p_list = [p.name for p in db_session.query(get_patient_db())]
        patient_selector = st.selectbox('**:red[Delete]**',
                                        options=p_list, index=0,
                                        key="delete_staff_selector", help=None,
                                        on_change=None, args=None, kwargs=None,
                                        placeholder="Select...", disabled=False,
                                        label_visibility="hidden")

        if st.button("**:red[Delete Patient]**"):
            delete_patient_entry(db_session, patient_selector)
            st.experimental_rerun()
    finally:
        db_session.close()


def view_staff():
    db_session = connect_database()
    try:
        staff_list = db_session.query(get_staff_db()).all()
        if staff_list:
            st.write("\n".join(
                [f"{staff.id} {staff.name} ({staff.role})" for staff in
                 staff_list]))
        else:
            st.write("No staff found.")
    finally:
        db_session.close()


def view_patients():
    db_session = connect_database()
    try:
        patient_list = db_session.query(get_patient_db()).all()
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
    finally:
        db_session.close()


def staff_data_editor():
    day_converter = CONVERTER_DAY
    night_converter = CONVERTER_NIGHT
    converter = TIME_CONVERTER
    day_set = set(CONVERTER_DAY)
    night_set = set(CONVERTER_NIGHT)
    hours = ALL_HOURS

    patient_table = allocations_db_tables()[1]

    db_session = connect_database()
    try:
        # Cache model classes once to avoid multiple FROMs and cartesian products
        staff_db = get_staff_db()
        patient_db = get_patient_db()

        # Construct the query to retrieve staff data from the database
        query = select(
            staff_db.name,
            staff_db.role,
            staff_db.gender,
            staff_db.assigned,
            staff_db.special_string,
            staff_db.special_list,
            staff_db.start,
            staff_db.end,
            staff_db.omit
        )

        patients_names = select(patient_db.name)

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
                                                 validate=r"^(?:([01][0-9]|2[0-3]):00(?:\s|$))+$"),
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

        # Sync from editor to DB using the cached model class
        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_names):
            if db_entry.name != df_entry:
                res = update_staff_entry(db_session, db_entry.id, name=df_entry)
                if not res['success']:
                    st.error(f"Update name failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_role):
            if db_entry.role != df_entry:
                res = update_staff_entry(db_session, db_entry.id, role=df_entry)
                if not res['success']:
                    st.error(f"Update role failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_gender):
            if db_entry.gender != df_entry:
                res = update_staff_entry(db_session, db_entry.id, gender=df_entry)
                if not res['success']:
                    st.error(f"Update gender failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_assign):
            if db_entry.assigned != df_entry:
                db_entry.assigned = df_entry

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_start):
            if db_entry.start != df_entry:
                db_entry.start = df_entry
                idx = hour_str_to_index(df_entry)
                if df_entry in day_set:
                    db_entry.start_time = day_converter[df_entry]
                elif df_entry in night_set:
                    db_entry.start_time = night_converter[df_entry]
                elif idx is not None:
                    db_entry.start_time = idx
                else:
                    db_entry.start_time = 0

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_end):
            if db_entry.end != df_entry:
                db_entry.end = df_entry
                idx = hour_str_to_index(df_entry)
                if df_entry in day_set:
                    db_entry.end_time = day_converter[df_entry]
                elif df_entry in night_set:
                    db_entry.end_time = night_converter[df_entry]
                elif idx is not None:
                    db_entry.end_time = idx
                else:
                    db_entry.end_time = 12

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_omit):
            if db_entry.omit != df_entry:
                db_entry.omit = df_entry
                db_entry.omit_time.clear()
                df_entry_list = df_entry.split()
                modified_times = times_list_to_indices(df_entry_list)
                for twelve_hour_range in modified_times:
                    db_entry.omit_time.append(twelve_hour_range)

        for db_entry, df_entry in zip(
                db_session.query(staff_db), df_special):
            if df_entry:
                if df_entry not in db_entry.special_list:
                    db_entry.special_list.append(df_entry)
                elif df_entry in db_entry.special_list:
                    db_entry.special_list.pop(
                        db_entry.special_list.index(df_entry))

        db_session.commit()
    finally:
        db_session.close()

    col1, col2 = st.columns(2)
    with col1:
        add_staff()
    with col2:
        delete_staff()


def patient_data_editor():
    db_session = connect_database()
    try:
        # Cache model classes once per call to avoid cartesian products
        patient_db = get_patient_db()
        staff_db = get_staff_db()

        # Construct query to retrieve patient data from the database
        query = select(
            patient_db.name,
            patient_db.observation_level,
            patient_db.obs_type,
            patient_db.room_number,
            patient_db.gender_req,
            patient_db.omit_staff_selector,
            patient_db.omit_staff
        )
        result = db_session.execute(query)
        patient_data = result.fetchall()

        # Construct query to retrieve staff data from the database
        staff_names = select(staff_db.name)
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
                db_session.query(patient_db), df_names):
            if db_entry.name != df_entry:
                res = update_patient_entry(db_session, db_entry.id, name=df_entry)
                if not res['success']:
                    st.error(f"Update name failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(patient_db), df_obs_level):
            if db_entry.observation_level != df_entry:
                res = update_patient_entry(db_session, db_entry.id, observation_level=df_entry)
                if not res['success']:
                    st.error(f"Update observation level failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(patient_db), df_obs_type):
            if db_entry.obs_type != df_entry:
                res = update_patient_entry(db_session, db_entry.id, obs_type=df_entry)
                if not res['success']:
                    st.error(f"Update obs type failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(patient_db), df_room_no):
            if db_entry.room_number != df_entry:
                res = update_patient_entry(db_session, db_entry.id, room_number=df_entry)
                if not res['success']:
                    st.error(f"Update room number failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(patient_db), df_gender_req):
            if db_entry.gender_req != df_entry:
                res = update_patient_entry(db_session, db_entry.id, gender_req=df_entry)
                if not res['success']:
                    st.error(f"Update gender req failed: {res['message']}")
                else:
                    st.write(res['message'])

        for db_entry, df_entry in zip(
                db_session.query(patient_db), df_selector):
            if df_entry:
                if df_entry not in db_entry.omit_staff:
                    db_entry.omit_staff.append(df_entry)
                elif df_entry in db_entry.omit_staff:
                    db_entry.omit_staff.pop(
                        db_entry.omit_staff.index(df_entry))

        db_session.commit()
    finally:
        db_session.close()

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
