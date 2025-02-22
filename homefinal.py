import pandas as pd
import streamlit as st
from datetime import datetime
import authlib

from streamlit_app import app_main

from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 

IMAGE_ADDRESS = "https://aboutibs.org/wp-content/uploads/sites/13/Diet-and-IBS-768x512.jpg"

# web app
st.title("IBD Control Helper")

st.image(IMAGE_ADDRESS, caption = "IBD Nutrition Importance")

def set_up_credentials():
    if 'credentials' not in st.session_state:
        jstr = st.secrets.get('GOOGLE_KEY')
        credentials = get_google_cloud_credentials(jstr)
        st.session_state['credentials']=credentials
    return st.session_state['credentials']

def main_code():
    
    creds=set_up_credentials()
    # Documentation for each key
    selected_keys = ['email', 'name']
    # Extract the key-value pairs from the dictionary
    selected_data = {key: st.experimental_user[key] for key in selected_keys}

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame([selected_data])

    
    st.subheader("User Information", divider=True)
    # Create the DataFrame
   

    # Display the DataFrame in Streamlit
    st.dataframe(df, hide_index=True)

    
config_auth_needed=st.secrets.get("AUTH_NEEDED","True").lower()=="true"

auth_needed=config_auth_needed and not st.experimental_user.is_logged_in

if auth_needed:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    # Display user name
    main_code()
    app_main()
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()