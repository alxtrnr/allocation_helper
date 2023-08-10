# 3 - Complete_Allocations.py

import streamlit as st
from solver import milo_solve


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title(":orange[Suggested Allocations]")
            pick = st.radio(label='**:green[Shift Selector]**',
                            options=['Days', 'Nights'],
                            index=0, key=None, help=None, on_change=None,
                            args=None, kwargs=None, disabled=False,
                            horizontal=True, label_visibility="visible")
            if pick == 'Days':
                milo_solve.solve_staff_allocation('D')
            else:
                milo_solve.solve_staff_allocation('n')

    except KeyError:
        st.warning('You are not logged in')


if __name__ == "__main__":
    app()
