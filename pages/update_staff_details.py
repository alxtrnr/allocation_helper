import streamlit as st

from authentication.authenticate import authenticate1
from database_utils.database_operations import update_staff
from database_utils.database_viewer import staff_to_assign


def app():
    authentication_status = authenticate1()
    if not authentication_status:
        return
    else:
        st.title("Update Staff")
        staff_to_assign()
        update_staff()


if __name__ == "__main__":
    app()
