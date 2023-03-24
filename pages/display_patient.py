import streamlit as st
from database_utils.database_viewer import display_patients


def app():
    st.title("Patients")
    display_patients()


if __name__ == "__main__":
    app()