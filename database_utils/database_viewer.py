# database_viewer.py

# from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, update

from database.database_creation import StaffTable, ObservationsTable
from sqlalchemy.orm import sessionmaker

# Create an engine to carry on with the table. This is the SQLite engine.
engine = create_engine('sqlite:///dev01.db', echo=False)

# Construct a sessionmaker object and bind it to the engine
Session = sessionmaker(bind=engine)
session = Session()


def display_staff():
    # Query the staff table
    conn = engine.connect()
    staff_data = pd.read_sql_query(session.query(StaffTable).statement, conn)

    # Drop the id column
    staff_data = staff_data.drop('id', axis=1)

    # Display the staff data in a tabular format without the index column
    st.dataframe(staff_data, width=1200, height=625)


def staff_to_assign():
    conn = engine.connect()
    staff_d = pd.read_sql_query(session.query(StaffTable).statement, conn)

    # Drop the id column
    staff_d = staff_d.drop('id', axis=1)
    staff_d = staff_d.drop("block", axis=1)
    staff_d = staff_d.drop('start_time', axis=1)
    staff_d = staff_d.drop('end_time', axis=1)
    staff_d = staff_d.drop('omit_time', axis=1)
    staff_d = staff_d.drop('duration', axis=1)

    edited_df = st.experimental_data_editor(data=staff_d, width=1200, height=625)
    for i, row in edited_df.iterrows():
        staff_name = row['name'].title()
        staff = session.query(StaffTable).filter_by(name=staff_name).first()
        staff.assigned = row.assigned
        session.commit()


def display_patients():
    # Query the patient table
    conn = engine.connect()
    patient_data = pd.read_sql_query(session.query(ObservationsTable).statement, conn)

    # Drop the id column
    patient_data = patient_data.drop('id', axis=1)

    # Display the patient data in a tabular format
    st.dataframe(patient_data, width=1200, height=625)
