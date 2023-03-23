import streamlit as st
from database_utils.database_viewer import staff_to_assign


def app():
    st.title("Staff")
    st.write("Assigned / unassigned staff to undertake observations")
    staff_to_assign()


app()
