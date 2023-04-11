import streamlit as st
import sys
import os

from authentication.authenticate import authenticate1

# This code adds the directory path of the parent directory of the current file to the list of system paths where Python
# searches for modules to import.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_utils.database_operations import add_staff


def app():
    authentication_status = authenticate1()
    if not authentication_status:
        return
    else:
        st.title("Add Staff Details")
        add_staff()


if __name__ == "__main__":
    app()
