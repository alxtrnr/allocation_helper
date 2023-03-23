import os
import sys

# This code adds the directory path of the parent directory of the current file to the list of system paths where Python
# searches for modules to import.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(page_title="Allocate Patient Observations", page_icon="🔭", layout="wide", menu_items=None)

from pages import home, add_patient_details, add_staff_details, delete_patient_details, delete_staff_details, \
    display_patient, \
    display_staff, update_patient_details, update_staff_details, \
    complete_allocations


def app():
    PAGES = {
        "Home": home,
        "Add Patient": add_patient_details,
        "Add Staff": add_staff_details,

        "Update Patient": update_patient_details,
        "Update Staff": update_staff_details,

        "Delete Patient": delete_patient_details,
        "Delete Staff": delete_staff_details,

        "View Patient": display_patient,
        "View Staff": display_staff,

        "Complete Allocations": complete_allocations,
    }
    # Use a beta_container to hide the pages in the sidebar
    with st.container():
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(PAGES.keys()))
        page = PAGES[selection]
        page.app()


app()
