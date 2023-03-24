import os
import sys

# add the path to the custom module to the system's path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from solver import milo_solve


def app():
    st.title("Suggested Allocations")
    shift = st.text_input("Day or Night shift d/N: ").upper()
    milo_solve.solve_staff_allocation(shift)


if __name__ == "__main__":
    app()
