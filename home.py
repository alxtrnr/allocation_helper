# home.py

from streamlit_authenticator import Authenticate
import streamlit as st

st.set_page_config(page_title="Allocation Helper", page_icon="🔭",
                   layout="wide",
                   menu_items={"Get help": "https://github.com/alxtrnr"
                                           "/spaa_streamlit/issues",
                               "Report a Bug": "https://github.com/alxtrnr"
                                               "/spaa_streamlit/issues",
                               "About": "https://github.com/alxtrnr"
                                        "/spaa_streamlit#readme"})


def introduction():
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


def authenticator_object():
    auth = Authenticate(
        dict(st.secrets['credentials']),
        st.secrets['cookie']['name'],
        st.secrets['cookie']['key'],
        st.secrets['cookie']['expiry_days'],
        st.secrets['preauthorized']
    )

    return auth


auth_object = authenticator_object()
ward_db = 'empty'


def authenticate_user():
    # This renders the login widget
    global ward_db
    name, authentication_status, username = auth_object.login('Login', 'sidebar')

    try:
        if username:
            # match user to their ward allocations database
            ward_db = st.secrets['user_db_dict'][username]
    except KeyError:
        ward_db = 'empty'

    # when there is no logged-in user
    if authentication_status is None:
        st.session_state.db = 'empty'
        ward_db = 'empty'

    # when the wrong username/password is entered
    elif authentication_status is False:
        st.error('Username/password is incorrect')
        for key in st.session_state.keys():
            del st.session_state[key]
        st.session_state.db = 'empty'
        ward_db = 'empty'

    # when the correct username/password is entered
    elif authentication_status:
        st.session_state.db = ward_db
        ward_db = ward_db

    return authentication_status, ward_db


if __name__ == "__main__":
    introduction()
    authenticate_user()
