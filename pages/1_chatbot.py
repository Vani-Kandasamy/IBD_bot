from openai import OpenAI
import streamlit as st
from text_graph import graph_streamer
from langchain_core.messages import AIMessage, HumanMessage
from google_integration import get_google_cloud_credentials, get_user_details, update_user_document
import pandas as pd 


IMAGE_ADDRESS = "https://upload.wikimedia.org/wikipedia/commons/1/1a/Irritable_bowel_syndrome.jpg"

def message_creator(list_of_messages: list) -> list:
    prompt_messages = []
    for message in list_of_messages:
        if message["role"] == "user":
            prompt_messages.append(HumanMessage(content = message["content"]))
        else:
            prompt_messages.append(AIMessage(content = message["content"]))

    return prompt_messages

# set the title
st.title("GastroGuide")
# set the image
st.image(IMAGE_ADDRESS, caption = 'IBS Disease Supporter')

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
