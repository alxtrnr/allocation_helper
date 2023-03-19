import streamlit as st
from database_utils.database_operations import delete_staff


def app():
    st.title("Delete Staff")
    delete_staff()


app()
