# 10 - Sign_Out.py

from streamlit_authenticator import Authenticate
import streamlit as st
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Allocate Patient Observations", page_icon="🔭",
                   layout="wide", menu_items={"Get help": None,
                                              "Report a Bug": None,
                                              "About": 'Alexander Turner 2023'})


def landing_blurb():
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


def authenticator_config():
    with open('config.yaml') as file:
        auth_config = yaml.load(file, Loader=SafeLoader)
        return auth_config


def authenticator_object():
    config = authenticator_config()

    # auth = Authenticate(
    #     dict(st.secrets['credentials']),
    #     st.secrets['cookie']['name'],
    #     st.secrets['cookie']['key'],
    #     st.secrets['cookie']['expiry_days'],
    #     st.secrets['preauthorized']
    # )

    auth = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # Initialize values in Session State
    if 'authenticator' not in st.session_state:
        st.session_state.authenticator = auth

    return auth


auth = authenticator_object()


def authenticate_user():
    # render_log_in_widget
    name, authentication_status, username = auth.login('Login', 'sidebar')

    # to match user to ward database
    ward_db = 'empty'
    user_db_dict = {
        "aturner": "dev01",
        "bturner": "dev02",
        'none': 'empty'
    }
    try:
        if username:
            ward_db = user_db_dict[username]
    except KeyError:
        ward_db = 'empty'

    # when there is no logged-in user
    if authentication_status is None:

        # st.warning('Please enter your username and password')
        for key in st.session_state.keys():
            del st.session_state[key]
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

    # st.write(st.session_state)
    # st.write(auth)

    return authentication_status, ward_db

    # st.write(st.session_state)
    # st.write(auth)


if __name__ == "__main__":
    landing_blurb()
    authenticate_user()
