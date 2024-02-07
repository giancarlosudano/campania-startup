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
import lib.common as common
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

try:
	st.set_page_config(page_title="Regione Campania - Ricerca Traiettorie", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Scelta Range Date")
	st.sidebar.image(os.path.join('images','logo.png'), use_column_width=True)
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
		load_dotenv()
		st.image(os.path.join('images','Slide1.JPG'), use_column_width=True)

		colonne = ['Data email', 'Oggetto', 'Da']
		df = pd.DataFrame(columns=colonne)
		i = 0
		for root, dirs, files in os.walk(os.path.join('ldv')):
			for name in dirs:
				file_msg = os.path.join('ldv', name, 'msg_data.txt')
				with open(file_msg, 'r') as file:
					content = file.read()
					from_pattern = r"from: (.+)"
					from_match = re.search(from_pattern, content)
					from_value = from_match.group(1) if from_match else None
					subject_pattern = r"subject: (.+)"
					subject_match = re.search(subject_pattern, content)
					subject_value = subject_match.group(1) if subject_match else None
					data_convertita = datetime.datetime.strptime(name, '%Y%m%d %H%M%S')
					if data_inizio <= data_convertita.date() <= data_fine:
						df.loc[i] = [name, subject_value, from_value]
				i += 1

		# select the columns you want the users to see
		gb = GridOptionsBuilder.from_dataframe(df)
		# configure selection
		gb.configure_selection(selection_mode="single", use_checkbox=True)
		gb.configure_side_bar()
		gridOptions = gb.build()

		data = AgGrid(df,
					gridOptions=gridOptions,
					enable_enterprise_modules=True,
					allow_unsafe_jscode=True,
					update_mode=GridUpdateMode.SELECTION_CHANGED,
					columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

		if st.button("Ricerca Traiettorie"):
			st.toast("TODO")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())