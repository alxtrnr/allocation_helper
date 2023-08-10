# 1 - Patients.py

import streamlit as st
from database_utils.database_operations import patient_data_editor


def app():
    if st.session_state['db'] == 'empty':
        st.markdown("# The Allocations Helper")
        st.divider()
        return st.warning('You are not logged in')
    else:
        st.title("Patients")
        patient_data_editor()


if __name__ == "__main__":
    app()
