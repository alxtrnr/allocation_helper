import streamlit as st
from database_utils.database_operations import update_patient


def app():
    st.title("Update Patient")
    update_patient()


app()
