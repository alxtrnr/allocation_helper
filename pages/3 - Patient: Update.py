# 3 - Patient: Update.py

import streamlit as st
from database_utils.database_operations import update_patient


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title("Update Patient")
            update_patient()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
