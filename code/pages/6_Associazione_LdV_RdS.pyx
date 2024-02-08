import streamlit as st
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
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Scelta della RDS con 'inferenza logica' di GPT4")
	st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)
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
		st.image(os.path.join('images','Slide6.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema ha raffinato al massimo i dati per una ricerca nel programma di trasporto della RDS ("richiesta di servizio") più appropriata.
A questo scopo **viene utilizzato GPT4 per sviluppare un algoritmo di ricerca**, che imposta le condizioni più adatte e stringenti, necessarie per la ricerca.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa. La ricerca tra i file di Orfeus è effettuata mediante tradizionale ricerca XML di libreria
- **Azure OpenAI**: Servizio di LLM in modalità GPT4-Turbo per l'automazione del processo di "ragionamento" per la ricerca della RDS più appropriata
""")

		# st.write("### Dati Attuali recuperati")

		# st.write("Origine (codice): " + st.session_state["box-01-orfeus"])
		# st.write("Destinazione (codice) " + st.session_state["box-01-orfeus"])
		# st.write("Codice Contratto (codice): " + st.session_state["box-01-orfeus"])
		# st.write("Data Lettera di Vettura: " + st.session_state["box-01-orfeus"])
		# st.write("Punti frontiera: " + st.session_state["box-01-orfeus"])
		# st.write("Massa totale: " + st.session_state["box-01-orfeus"])
		# st.write("Lunghezza totale: " + st.session_state["box-01-orfeus"])
  
		import pandas as pd
		excel_path = os.path.join('ldv', 'rds-test.xlsx')
		df = pd.read_excel(excel_path)

		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode		
		gb = GridOptionsBuilder.from_dataframe(df)
		gb.configure_side_bar()
		gridOptions = gb.build()

		data = AgGrid(df,
					gridOptions=gridOptions,
					enable_enterprise_modules=True,
					allow_unsafe_jscode=True,
					update_mode=GridUpdateMode.SELECTION_CHANGED,
					columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

# Origine colonne G H I
# Rete Mittente
# Stazione Mittente
# Des. Stazione Mittente
# Destinazione O P Q
# Rete Destinataria
# Stazione Destinataria
# Des. Stazione Destinataria
# Data RDS (C)
# Contratto (D)
# Mittente/Destinatario (TODO) (F)
# Sequenze PDF (punti di frontiera)
# Sequenza IF (Z)

		st.write("""Prompt GPT4-Turbo
data la lista di servizi ferroviari in tabella

scegli tutte le righe che rispettano questi requisiti:
- la colonna "Rete Mittente" deve essere uguale a **80**
- la colonna "Stazione Mittente" deve essere uguale a **637702**
- la colonna "Rete Destinataria" deve essere uguale a **83**
- la colonna "Stazione Mittente" deve essere uguale a **024323**
- il contratto deve essere uguale a **IN903417**
- la colonna "Data RDS" essere uguale a **07-11-2023** o successiva al massimo di 3 giorni, ignora l'orario

""")
		input = """data questa lista di servizi ferroviari

| ID RDS                          | ID RC       | DATA RDS            | CONTRATTO | Cliente Titolare | Descrizione Cliente Titolare                            | Rete Mittente | Stazione Mittente | Des. Stazione Mittente                                       | Rete Mitt. Effett. | Impianto Mitt. Effett. | Des.Impianto Mitt. Effett.                                   | Raccordo Mittente | Des. Raccordo Mittente                    | Rete Destinataria | Stazione Destinataria | Des. Stazione Destinataria                                   | Rete Dest. Effett. | Impianto Dest. Effett. | Des. Impianto Dest. Effett.                                  | Raccordo Destinatario | Des. Raccordo Destinatario               | IF /Stazione di contatto | Des. IF/Stazione di Contatto                                 | Sequenza ordinata PDF | Sequenza delle IF      | Peso MAX Ammesso | Lunghezza MAX Ammessa | RID SI/NO |
|---------------------------------|-------------|---------------------|-----------|------------------|---------------------------------------------------------|---------------|-------------------|--------------------------------------------------------------|--------------------|------------------------|--------------------------------------------------------------|-------------------|-------------------------------------------|-------------------|-----------------------|--------------------------------------------------------------|--------------------|------------------------|--------------------------------------------------------------|-----------------------|------------------------------------------|--------------------------|--------------------------------------------------------------|-----------------------|------------------------|------------------|-----------------------|-----------|
| 1-111565461_2023-11-07_09:30:00 | 1-111565461 | 07-11-2023 00:00:00 | IN064953  | 057422           | FRET SNCF                                               | 83            | 015222            | LECCO MAGGIANICO                                             | 83                 | 015222                 | LECCO MAGGIANICO                                             | 00BAT             | BATTAZZA SPA                              | 87                | 191015                | Ebange                                                       | 87                 | 191015                 | Ebange                                                       |                       |                                          | 3356                     | BLS Cargo AG                                                 | 259, 321              | 2183, 3356, 2187       | 600              | 400                   | NO        |
| 1-355201136_2023-11-07_21:10:00 | 1-355201136 | 07-11-2023 00:00:00 | IN916303  | 057137           | HUPAC INTERMODAL SA                                     | 83            | 018127            | BRESCIA FASCIO MERCI                                         | 83                 | 018127                 | BRESCIA FASCIO MERCI                                         | 09206             | RFI - TERMINALI ITALIA                    | 80                | 146712                | Singen (Hohentwiel) Ubf                                      | 80                 | 146712                 | Singen (Hohentwiel) Ubf                                      |                       |                                          | 2185                     | SCHWEIZERISCHE BUNDESBAHNEN                                  | 493, 321              | 2183, 2185, 2180       | 1600             | 535                   | NO        |
| 1-90330817_2023-11-07_06:21:00  | 1-90330817  | 07-11-2023 00:00:00 | 20328240  | 017305           | CNH ITALIA S.P.A.                                       | 83            | 050120            | CASTELGUELFO                                                 | 83                 | 050120                 | CASTELGUELFO                                                 | 00CEP             | INTERP. PARMA - CEPIM                     | 83                | 072025                | JESI                                                         | 83                 | 050328                 | MODENA                                                       | 00RAC                 | CNH ITALIA SPA - NEW HOLLAND             |                          |                                                              |                       |                        | 800              | 470                   | NO        |

scegli le righe che rispettano questi requisiti in modo più preciso possibile:
- la colonna "Rete Mittente" deve essere uguale a 80
- la colonna "Stazione Mittente" deve essere uguale a 637702
- la colonna "Rete Destinataria" deve essere uguale a 83
- la colonna "Stazione Mittente" deve essere uguale a 024323
- il contratto deve essere uguale a IN903417
- la colonna "Data RDS" deve essere uguale a **07-11-2023**, ignora l'orario

Mostra il tuo ragionamento

Risposta:
"""

		container_stream = st.container()

		llm = AzureChatOpenAI(
			azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
			api_key=os.getenv("AZURE_OPENAI_KEY"),
			api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
			max_tokens=1000, 
			temperature=0,
			deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
			model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
			streaming=True, callbacks=[StreamlitCallbackHandler(container_stream)]
		)

		prompt = ChatPromptTemplate.from_messages([
			("system", "You are an AI assistant."),
			("user", "{input}")
		])

		output_parser = StrOutputParser()
		chain = prompt | llm | output_parser
		response = chain.invoke({"input": input})
		container_stream.empty()

		if st.button("Conferma i valori"):
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())