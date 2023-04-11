import streamlit as st

from authentication.authenticate import authenticate1
from database_utils.database_operations import delete_staff


def app():
    authentication_status = authenticate1()
    if not authentication_status:
        return
    else:
        st.title("Delete Staff")
        delete_staff()


if __name__ == "__main__":
    app()
