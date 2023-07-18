# 2 - Patient: Add.py

import streamlit as st
from database_utils.database_operations import add_patient


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            st.warning('You are not logged in')
        else:
            st.title("Add Patient Details")
            st.markdown("Only add patients who are on enhanced observations. "
                        "Observation level is 1-4. Patients in seclusion "
                        "should be added as observation level 1 (1:1)")
            add_patient()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
