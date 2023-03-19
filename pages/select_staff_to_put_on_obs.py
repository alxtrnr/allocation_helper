import streamlit as st
from database_utils.database_operations import assign_on_obs


def app():
    st.title("Assign Staff to Observations")
    assign_on_obs()


app()
