import streamlit as st
from database_utils.database_operations import update_staff
from database_utils.database_viewer import staff_to_assign


def app():
    st.title("Update Staff")
    staff_to_assign()
    update_staff()


if __name__ == "__main__":
    app()
