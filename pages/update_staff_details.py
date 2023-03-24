import streamlit as st
from database_utils.database_operations import update_staff


def app():
    st.title("Update Staff")
    update_staff()


if __name__ == "__main__":
    app()
