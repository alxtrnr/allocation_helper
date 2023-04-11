import yaml
from streamlit_authenticator import Authenticate
import streamlit as st
from yaml import SafeLoader


def authenticate1():
    # with open('config.yaml') as file:
    #     config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        dict(st.secrets['credentials']),
        st.secrets['cookie']['name'],
        st.secrets['cookie']['key'],
        st.secrets['cookie']['expiry_days'],
        st.secrets['preauthorized']
    )

    # authenticator = Authenticate(
    #     config['credentials'],
    #     config['cookie']['name'],
    #     config['cookie']['key'],
    #     config['cookie']['expiry_days'],
    #     config['preauthorized']
    # )

    if 'authenticator' not in st.session_state:
        st.session_state.authenticator = authenticator

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status is None:
        st.warning('Please enter your username and password')
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is True:
        st.success(f'{name.upper()} is logged in')
        authenticator.logout('Logout', 'main')
    return authentication_status


if __name__ == "__main__":
    authenticate1()
