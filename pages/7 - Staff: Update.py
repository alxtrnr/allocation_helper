# 7 - Staff: Update.py

import streamlit as st
from database_utils.database_operations import update_staff
from database_utils.database_operations import editable_staff_table


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning(f'You are not logged in')
        else:
            st.title("Update Staff")
            editable_staff_table()
            update_staff()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
