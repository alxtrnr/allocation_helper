import streamlit as st

st.set_page_config(page_title="Allocate Patient Observations", page_icon="🔭",
                   layout="wide", menu_items=None)


def app():
    st.markdown("# The Allocations Helper")
    st.markdown(
        "### Use the Allocations Helper to assist with allocating staff to"
        " patient observations.")
    st.divider()
    container = st.container()
    container.write("")  # used as a spacer
    col1, col2 = st.columns(2)

    col1.markdown("""
    #### Functionality includes - 
    st.markdown("""
    * ##### Create, update and delete patient and staff details
    * ##### View patient and staff details
    * ##### Assign staff to complete observations
    * ##### Generate and view suggested allocations
    * ##### Download suggested allocations. These can be tweaked as needed.
    """)

    col2.markdown("""
    #### Generate allocations that factor in -     
    * ##### Patient observation level (generals, 1:1, 2:1, 3:1, 4:1)
    * ##### Patient/staff matching as needed
    * ##### Staff excluded from observations at certain times as needed
    * ##### No allocation being longer than two contiguous hours
    * ##### Time off for breaks according to hours worked
    * ##### Shift patterns - nights/days
    * ##### Staff working hours - long day/night or custom hours
    """)

    st.divider()


app()
