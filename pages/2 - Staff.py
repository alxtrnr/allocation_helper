# 2 - Staff.py

import streamlit as st
from database_utils.database_operations import staff_data_editor


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title(":orange[Staff]")
            st.markdown("**:green[Hover over each column heading for help]**")
            staff_data_editor()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
