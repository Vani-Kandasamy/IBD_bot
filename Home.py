import pandas as pd
import streamlit as st
from datetime import datetime
import authlib

from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 

IMAGE_ADDRESS = "https://aboutibs.org/wp-content/uploads/sites/13/Diet-and-IBS-768x512.jpg"

# web app
st.title("IBD Control Helper")

st.image(IMAGE_ADDRESS, caption = "IBD Nutrition Importance")

if not st.experimental_user.is_logged_in:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    # Display user name
    st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
