import streamlit as st
from database_utils.database_operations import editable_staff_table


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title("Staff")
            st.write("Use the checkbox to change status of staff being "
                     "assigned unassigned for observations.")
            editable_staff_table()
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
