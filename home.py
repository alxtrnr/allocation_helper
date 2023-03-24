import os
import sys

# This code adds the directory path of the parent directory of the current file to the list of system paths where Python
# searches for modules to import.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(page_title="Allocate Patient Observations", page_icon="🔭", layout="wide", menu_items=None)

from pages import add_patient_details, add_staff_details, delete_patient_details, delete_staff_details, \
    display_patient, display_staff, update_patient_details, update_staff_details, complete_allocations


def app():
    st.markdown("# The Allocations App")
    st.markdown("""
    * ##### Create, update and delete patient and staff details 
    * ##### View patient and staff details
    * ##### Assign staff to complete observations 
    * ##### Complete the allocations
    * ##### View the allocations
    
    
    Staff are allocated to patients according to each patients observation level. Staff are assigned by default for 12 
    hours. This can be changed for each staff member according to their availability. Time for breaks is allocated 
    automatically though may manually be assigned by the user. The same functionality allows any time needed for other 
    tasks such as appointments, meetings, etc to be set. Staff are never assigned for more than two consecutive hours. 
    Requirements for staff of a specific gender to undertake a specific patients observations can be factored in. 
    Requirements to exclude a staff member from a specific patient's observations may also be set. Staff may also be 
    assigned to undertake observations for named patients only.   
    """)


    PAGES = {
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


app()
