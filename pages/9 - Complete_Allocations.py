# 9 - Complete_Allocations.py

import streamlit as st
from solver import milo_solve


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title("Suggested Allocations")
            shift = st.text_input("Day or Night shift d/N: ").upper()
            milo_solve.solve_staff_allocation(shift)
    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
