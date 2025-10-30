# 3 - Complete_Allocations.py

import streamlit as st
from solver import milo_solve
from services.staff_service import check_allocation_feasibility
from database_utils.database_operations import connect_database


def app():
    try:
        if st.session_state['db'] == 'empty':
            st.markdown("# The Allocations Helper")
            st.divider()
            return st.warning('You are not logged in')
        else:
            st.title(":orange[Suggested Allocations]")
            # Check allocation feasibility before allow solve
            with connect_database() as db_session:
                feas = check_allocation_feasibility(db_session)
                if not feas['success']:
                    st.error(feas['message'])
                    for w in feas['warnings']:
                        st.warning(w)
                    st.stop()
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
