import streamlit as st
from database_utils.database_viewer import display_staff


def app():
    st.title("Staff")
    display_staff()


app()
