import streamlit as st
st.set_page_config(page_title="Allocate Patient Observations", page_icon="🔭", layout="wide", menu_items=None)


def app():
    st.markdown("# The Allocations App")
    st.markdown("""
    * ##### Create, update and delete patient and staff details
    * ##### View patient and staff details
    * ##### Assign staff to complete observations
    * ##### Complete the allocations
    * ##### View the allocations


    Staff are allocated to patients according to each patients observation level. Staff are assigned by default for 12
    hours. You may change this for each member of staff according to their availability. Time for breaks is allocated
    automatically though may also be manually assigned. The same functionality allows any time needed for other
    tasks such as appointments, meetings, etc to be set. Staff are never assigned for more than two consecutive hours.
    Requirements for staff of a specific gender to undertake a specific patients observations can be factored in.
    A requirement to exclude a staff member from a specific patient's observations may also be set. Cherry-picking
    enables staff to be assigned observations for named patients only.
    """)


app()
