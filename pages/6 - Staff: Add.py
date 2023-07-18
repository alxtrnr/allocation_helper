# ass_staff_details.py

import streamlit as st
from database_utils.database_operations import add_staff


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title("Add Staff Details")
            add_staff()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
