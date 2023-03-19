import streamlit as st
from solver.milo_solve import solve_staff_allocation

def app():
    st.title("Schedule Results")
    solve_staff_allocation()



app()
