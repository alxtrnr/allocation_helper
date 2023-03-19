import streamlit as st
from database_utils.database_operations import delete_patient


def app():
    st.title("Delete Patient")
    delete_patient()


app()
