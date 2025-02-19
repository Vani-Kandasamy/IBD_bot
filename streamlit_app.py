import streamlit as st
from google_integration import get_google_cloud_credentials, fetch_prompts, update_prompt_by_name
import pandas as pd 

def set_up_credentials():
    if 'credentials' not in st.session_state:
        jstr = st.secrets.get('GOOGLE_KEY')
        credentials = get_google_cloud_credentials(jstr)
        st.session_state['credentials']=credentials
    return st.session_state['credentials']

def show_all(creds):
    s1=fetch_prompts(creds)
    df=pd.DataFrame(s1)
    st.dataframe(df, hide_index=True)

def show_one_detail(creds):
    s1=fetch_prompts(creds)
    prompt_names=[s.get('prompt_name') for s in s1]
    prompt_values=[s.get('prompt_value') for s in s1]
    prompt_map=dict(zip(prompt_names,prompt_values))
    option = st.selectbox("Prompt",prompt_names,index=None)
    if option:
        prv=prompt_map[option]
        st.text(f"{prv}")


def update_one(creds):
    prompt_name=st.text_input("Prompt name")
    prompt_value=st.text_area("Prompt text")
    if st.button("Upsert"):
        s=update_prompt_by_name(creds, prompt_name,prompt_value)
        st.write(s)

def app_main():
    creds=set_up_credentials()
    col1,col2,col3=st.tabs(['List','Review','Upsert'])
    with col1:
        show_all(creds)
    with col2:
        show_one_detail(creds)
    with col3:
        update_one(creds)
