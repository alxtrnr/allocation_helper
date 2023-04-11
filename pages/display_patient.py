import streamlit as st

from authentication.authenticate import authenticate1
from database_utils.database_viewer import display_patients


def app():
    authentication_status = authenticate1()
    if not authentication_status:
        return
    else:
        st.title("Patients")
        display_patients()


if __name__ == "__main__":
    app()
