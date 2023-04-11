import streamlit as st
from database_utils.database_viewer import staff_to_assign
from authentication.authenticate import authenticate1


def app():
    authentication_status = authenticate1()

    if not authentication_status:
        return
    else:
        st.title("Staff")
        st.write("Use the checkbox to change status of staff being assigned / unassigned for observations.")
        staff_to_assign()


if __name__ == "__main__":
    app()
