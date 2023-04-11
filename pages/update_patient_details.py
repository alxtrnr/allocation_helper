import streamlit as st

from authentication.authenticate import authenticate1
from database_utils.database_operations import update_patient


def app():
    authentication_status = authenticate1()
    if not authentication_status:
        return
    else:
        st.title("Update Patient")
        update_patient()


if __name__ == "__main__":
    app()
