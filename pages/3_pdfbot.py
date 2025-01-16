import streamlit as st
from pdf_graph import graph_streamer, extract_text_from_pdf, helper_graph
from langchain_core.messages import AIMessage, HumanMessage

PDF_NAME = "pdfchatuploaded.pdf"

def message_creator(list_of_messages: list) -> list:
    prompt_messages = []
    for message in list_of_messages:
        if message["role"] == "user":
            prompt_messages.append(HumanMessage(content = message["content"]))
        else:
            prompt_messages.append(AIMessage(content = message["content"]))

    return prompt_messages

st.title("PDF Chat")

st.subheader("Chat with Us 🤖")

def empty_message_list():
   st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", on_change=empty_message_list)

if uploaded_file:
    # save the file
    with open(PDF_NAME, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # read the texts and display
    # extract_data = extract_text_from_pdf(PDF_NAME)
    # # disply the pdf
    # st.subheader("Extracted Data")
    # st.markdown(extract_data)

    # # check pdf related to IBD or not
    # # execute the graph
    # with st.spinner("Analysing............"):
    #     get_content = helper_graph.invoke({"pdf_path": PDF_NAME})
    # # display content
    # if get_content["accept_content"]:
    #     st.subheader("PDF Information")
    #     st.write(get_content["content"])
    # else:
    #     st.subheader("Ooopss!! Not Related to IBD!")
    #     st.write(get_content["content"])

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
        response = st.write_stream(graph_streamer(PDF_NAME, message_list))
    st.session_state.messages.append({"role": "assistant", "content": response})