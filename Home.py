import pandas as pd
import streamlit as st
from datetime import datetime
import authlib
import chatbot
import imagebot
import pdfbot

from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 

IMAGE_ADDRESS = "https://aboutibs.org/wp-content/uploads/sites/13/Diet-and-IBS-768x512.jpg"

# web app
st.title("IBD Control Helper")

st.image(IMAGE_ADDRESS, caption = "IBD Nutrition Importance")

if not st.experimental_user.is_logged_in:
    st.warning("Please log in to access the services.")
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    # Display user name
    st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()

    with st.container():
        tab1, tab2, tab3 = st.tabs(["ChatBot", "ImageBot", "PDFBot"])

        # Use imported display functions in each tab
        with tab1:
            chatbot.chat_bot()

        with tab2:
            imagebot.image_bot()

        with tab3:
            pdfbot.pdf_bot()


