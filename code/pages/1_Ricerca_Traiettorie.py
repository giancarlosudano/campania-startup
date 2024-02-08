import streamlit as st
import streamlit_authenticator as stauth
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import StreamlitCallbackHandler
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import datetime
import os
import re
import pandas as pd
import streamlit as st
import yaml
from yaml.loader import SafeLoader


def get_traiettorie():
	try:
		llm = AzureChatOpenAI(
			azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
			api_key=os.getenv("AZURE_OPENAI_KEY"),
			api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
			max_tokens=1000,
			temperature=0,
			deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
			model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
			streaming=False
		)

		with open(os.path.join('data', 'traiettorie.md'), 'r', encoding='utf-8') as file:
			tabella = file.read()

		prompt_composed = """Data la seguente descrizione di una attività delimitata da ###
identifica dalla tabella fornita la lista delle righe che si avvicinano maggiormente alla descrizione fornita.

attività:
### 
{input}
###

Tabella:
{tabella}

- Nella risposta fornisci sempre il contenuto di tutte le colonne della tabella per ciascuna riga identificata.

Risposta:
"""
		prompt = ChatPromptTemplate.from_messages([
			("system", "You are an AI assistant."),
			("user", prompt_composed)
		])

		output_parser = StrOutputParser()
		chain = prompt | llm | output_parser
		response = chain.invoke({"input": st.session_state['descrizione'], "tabella": tabella})
		st.write(response)

	except Exception as e:
		st.error(traceback.format_exc())

try:
	st.set_page_config(page_title="Regione Campania - Ricerca Traiettorie", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Ricerca traiettorie")
	load_dotenv()
	st.sidebar.image(os.path.join('images','logo.png'), use_column_width=True)

	st.write(os.getenv("AZURE_OPENAI_BASE"))
	# with open('config.yaml') as file:
	# 	config = yaml.load(file, Loader=SafeLoader)

	# authenticator = stauth.Authenticate(
	# 	config['credentials'],
	# 	config['cookie']['name'],
	# 	config['cookie']['key'],
	# 	config['cookie']['expiry_days'],
	# 	config['preauthorized']
	# )

	# if st.session_state["authentication_status"]:

	st.text_area("Descrizione", key="descrizione", height=200)
	container_button = st.container()
	container_streaming = st.container()
	container_response = st.container()
	container_button.button("Ricerca Traiettorie...", key="button", on_click=get_traiettorie)
	
	# elif st.session_state["authentication_status"] is False:
	# 	st.error('Username/password is incorrect')
	# elif st.session_state["authentication_status"] is None:
	# 	st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())