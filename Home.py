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
    try:
        # Retrieve the authorization code from the URL
        code = st.experimental_get_query_params().get('code')

        # Exchange the authorization code for an access token
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        body = {
            'grant_type': 'authorization_code',
            'client_id': AUTH0_CLIENT_ID,
            'client_secret': AUTH0_CLIENT_SECRET,
            'redirect_uri': AUTH0_CALLBACK_URL,
            'code': code
        }

        response = requests.post(token_url, data=body, headers=headers)
        response.raise_for_status()
        token_info = response.json()

        # Retrieve user info with the access token
        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        user_response = requests.get(userinfo_url, headers={'Authorization': f"Bearer {token_info['access_token']}"})
        user_response.raise_for_status()
        user_info = user_response.json()

        return token_info, user_info

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred during login: {e}")
        return None, None

def main():
    st.title("Streamlit App with Auth0 Authentication")

    # Auth0 login URL
    login_url = (
        f"https://{AUTH0_DOMAIN}/authorize"
        f"?response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid profile email"
        f"&audience={API_AUDIENCE}"
    )

    if 'user_info' not in st.session_state:
        st.markdown(f"[Login with Auth0]({login_url})")

        if 'code' in st.experimental_get_query_params():
            token_info, user_info = login_callback()
            if user_info:
                st.session_state['user_info'] = user_info

    if 'user_info' in st.session_state:
        st.write("You are logged in!")
        #st.write(st.session_state['user_info'])

        

        with st.container():
            tab1, tab2, tab3 = st.tabs(["ChatBot", "ImageBot", "PDFBot"])

            # Use imported display functions in each tab
            with tab1:
                chatbot.chat_bot()

            with tab2:
                imagebot.image_bot()

            with tab3:
                pdfbot.pdf_bot()

        if st.button("Log out"):
            st.session_state.clear()

if __name__ == "__main__":
    main()
