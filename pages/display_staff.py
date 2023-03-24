import streamlit as st
from database_utils.database_viewer import staff_to_assign


def app():
    st.title("Staff")
    st.write("Use the checkbox to change status of staff being assigned / unassigned for observations.")
    staff_to_assign()


if __name__ == "__main__":
    app()
