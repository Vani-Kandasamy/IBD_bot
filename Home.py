import pandas as pd
import streamlit as st
from datetime import datetime
import authlib
import chatbot
import imagebot
import pdfbot

from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 

import requests

# Access Auth0 configuration from secrets
AUTH0_DOMAIN = st.secrets["auth0_domain"]
AUTH0_CLIENT_ID = st.secrets["auth0_client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0_client_secret"]
AUTH0_CALLBACK_URL = st.secrets["auth0_callback_url"]
API_AUDIENCE = st.secrets["api_audience"]

IMAGE_ADDRESS = "https://aboutibs.org/wp-content/uploads/sites/13/Diet-and-IBS-768x512.jpg"

# web app
st.title("IBD Control Helper")

st.image(IMAGE_ADDRESS, caption = "IBD Nutrition Importance")

def login_callback():
    # This function should handle obtaining the access token and user info
    try:
        # Fetching token
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        body = {
            'grant_type': 'authorization_code',
            'client_id': AUTH0_CLIENT_ID,
            'client_secret': AUTH0_CLIENT_SECRET,
            'redirect_uri': AUTH0_CALLBACK_URL,
            'code': st.experimental_get_query_params().get('code')
        }

        response = requests.post(token_url, data=body, headers=headers)
        token_info = response.json()

        # Fetch user info
        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        user_response = requests.get(userinfo_url, headers={'Authorization': f"Bearer {token_info['access_token']}"})
        user_info = user_response.json()

        return token_info, user_info

    except Exception as e:
        st.error(f"An error occurred during login: {e}")
        return None, None

def main():

    
    st.title("Streamlit App with Auth0 Authentication")

    # Example login URL (needs the correct application state and nonce handling in a real app)
    login_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid profile email&audience={API_AUDIENCE}"


    if 'user_info' not in st.session_state:
        st.warning("Please log in to access the services.")
        st.markdown(f"[Login with Auth0]({login_url})")   
        #st.sidebar.button(f"[Login with Auth0]({login_url})")
        #st.login()

        if 'code' in st.experimental_get_query_params():
            _, user_info = login_callback()
            st.session_state['user_info'] = user_info

    if 'user_info' in st.session_state:
        #st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
        st.write("You are logged in!")
        st.write(st.session_state['user_info'])
        st.button("Log out", on_click=lambda: st.session_state.clear())
    
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

if __name__ == "__main__":
    main()


