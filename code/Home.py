import sys
import streamlit as st
import os
import logging
from dotenv import load_dotenv
import streamlit_authenticator as stauth

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
st.set_page_config(page_title="Regione Campania - Ricerca traiettorie", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

st.title("Regione Campania - Ricerca traiettorie")
st.sidebar.image(os.path.join('images','logo.png'), use_column_width=True)

import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login(location='main')

if username == 'smith@regionecampania.com':
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "John Smith"

    st.write(f'Welcome *{st.session_state["name"]}*, you are an **admin**.')
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')