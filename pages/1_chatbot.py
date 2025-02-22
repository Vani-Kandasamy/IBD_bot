from openai import OpenAI
import streamlit as st
from text_graph import graph_streamer
from langchain_core.messages import AIMessage, HumanMessage
from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 
from google.cloud import firestore


IMAGE_ADDRESS = "https://upload.wikimedia.org/wikipedia/commons/1/1a/Irritable_bowel_syndrome.jpg"

def message_creator(list_of_messages: list) -> list:
    prompt_messages = []
    for message in list_of_messages:
        if message["role"] == "user":
            prompt_messages.append(HumanMessage(content = message["content"]))
        else:
            prompt_messages.append(AIMessage(content = message["content"]))

    return prompt_messages

def set_up_credentials():
    if 'credentials' not in st.session_state:
        service_account_info = st.secrets["gcp_service_account"]
        credentials = get_google_cloud_credentials(service_account_info)
        st.session_state['credentials']=credentials
    return st.session_state['credentials']

def get_db(credentials):
    # Initialize the Firestore client using credentials
    #credentials = set_up_credentials()
    db = firestore.Client(credentials=credentials)
    return db

def display(db):
    # Retrieve user details from Firestore
    user_details = get_user_details(db, user_email)
    if user_details:
        #st.subheader("User Information")
        st.write(user_details)

def main_code():
    
    creds=set_up_credentials()
    db = get_db(creds)

    # Assuming 'st.experimental_user' is a valid object with user details
    user_email = st.experimental_user["email"]
    user_name = st.experimental_user["name"]
    
    # set the title
    st.title("GastroGuide")
    # set the image
    st.image(IMAGE_ADDRESS, caption = 'IBS Disease Supporter')

    # Create tabs for login and data viewing
    tabs = st.tabs(["Chat", "User Data"])

    with tabs[0]:
        st.subheader("Chat with Us 🤖")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # input from the user
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # content manager for displaying appropriate message
            with st.chat_message("assistant"):
                message_list = message_creator(st.session_state.messages)
                print("Message List", message_list)
                response = st.write_stream(graph_streamer(message_list))
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Assuming user_email and user_name are set correctly in session
            update_user_document(db, user_email, user_name, prompt, response)

    with tabs[1]:   
        st.subheader("Your Data")
        if st.session_state.get('logged_in'):
            display(db)
        else:
            st.warning("You must log in to access this tab.")

if __name__ == "__main__":
    main_code()


