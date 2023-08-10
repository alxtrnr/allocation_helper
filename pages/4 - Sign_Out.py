import streamlit as st
from home import authenticate_user
from home import authenticator_object


def app():
    auth = authenticator_object()
    if not st.session_state.authentication_status:
        st.markdown("# The Allocations Helper")
        st.divider()
        st.warning('You are not logged in')
    else:
        st.markdown("# The Allocations Helper")
        st.divider()
        st.markdown(f'##### Name: {st.session_state.name}')
        st.markdown(f'##### Username: {st.session_state.username}')
        st.markdown(f'##### Ward: {st.session_state.db}')
        st.markdown(f'##### Logged in: {st.session_state.authentication_status}')
        st.divider()
        auth.logout('Sign Out', 'main', key='sign_out_page')


if __name__ == "__main__":
    app()
