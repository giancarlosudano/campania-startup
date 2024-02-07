import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import base64
import datetime
import glob
import json
import openai
import os
import requests
import sys
import re

try:
	st.set_page_config(page_title="Regione Campania - Conversione Tabella in markdown", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Creazione Tabella Traiettorie in markdown")
	st.sidebar.image(os.path.join('images','logo.png'), use_column_width=True)
	load_dotenv()

	import streamlit_authenticator as stauth
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

	if st.session_state["authentication_status"]:
		excel_path = os.path.join('data', 'traiettorie.xlsx')
		markdown_path = os.path.join('data', 'traiettorie.md')

		with st.form("my_form"):
			submitted = st.form_submit_button("Conferma valori")
  
			if submitted:
				data = pd.read_excel(excel_path)
				compact_markdown_table = data.to_markdown(index=False, tablefmt="pipe")
				with open(markdown_path, 'w', encoding='utf-8') as file:
					file.write(compact_markdown_table)
				st.toast("Tabella convertita")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())