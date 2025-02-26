from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from typing import  Annotated
import operator
from pinecone import Pinecone
from openai import OpenAI
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

from google_integration import get_google_cloud_credentials, get_user_details, update_user_document, get_user_field
import pandas as pd 
from google.cloud import firestore


import streamlit as st
import os

from google_integration import get_user_field

os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"]= st.secrets["PINECONE_API_KEY"]
os.environ["INDEX_HOST"]= st.secrets["INDEX_HOST"]

# constants
TEXT_MODEL = "text-embedding-ada-002"
NAMESPACE_KEY = "Keya"
ANSWER_INSTRUCTIONS = """
You are an expert nutritionist specializing in advising IBD patients.

Your responses are generated based on a combination of knowledge base and user query logs retrieved from the Firestore database.

Your goal is to answer the question posed by the user effectively and accurately.

Follow these guidelines when interacting with the user:

1. Determine whether the user's input is a question or a greeting.
   - If it's a greeting, respond with an appropriate and friendly greeting.

2. If the user's input is a question, follow these steps to provide your answer:
   - Retrieve relevant context from the knowledge base and query logs in Firestore.
   - Use only the information provided within these sources to form your response.

When answering questions:

1. Base your response solely on the context retrieved.
2. Do not introduce external information or assumptions beyond what is explicitly provided.
3. Ensure clarity and empathy in your communication, aligning with your role as an expert advisor.
"""

def format_logs_for_context(query_logs):
    # Convert logs to a string format suitable for context
    if not query_logs:
        return "No recent user queries found."

    formatted_logs = ["Recent User Queries:"]
    for log in query_logs:
        # Assuming each log contains a 'query' and 'timestamp'
        formatted_logs.append(f"- {log['timestamp']}: {log['query']}")

    return "\n".join(formatted_logs)

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

creds=set_up_credentials()
db = get_db(creds)

user_email = st.user["email"]

# Retrieve query logs for the user
query_logs = get_user_field(db, user_email)

logs_text = format_logs_for_context(query_logs)

# Combine logs and knowledge context
ANSWER_INSTRUCTIONS = f"{logs_text}\n{ANSWER_INSTRUCTIONS}"

# set the openai model
llm = ChatOpenAI(model="gpt-4o", temperature=0)
# create client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# pinecone setup
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(host=os.environ["INDEX_HOST"])

# this is be default has the messages and add_messages reducers (different from colab)
class BotState(MessagesState):
    context: Annotated[list, operator.add]
    answer: str

def get_openai_embeddings(text: str) -> list[float]:
    response = client.embeddings.create(input=f"{text}", model=TEXT_MODEL)

    return response.data[0].embedding


# function query similar chunks
def query_response(query_embedding, k = 2, namespace_ = NAMESPACE_KEY):
    query_response = index.query(
        namespace=namespace_,
        vector=query_embedding,
        top_k=k,
        include_values=False,
        include_metadata=True,
    )

    return query_response

def content_extractor(similar_data):
    top_values = similar_data["matches"]
    # get the text out
    text_content = [sub_content["metadata"]["text"] for sub_content in top_values]
    return " ".join(text_content)


def get_similar_context(question: str):
    # get the query embeddings
    quer_embed_data = get_openai_embeddings(question)

    # query the similar chunks
    similar_chunks = query_response(quer_embed_data)

    # extract the similar text data
    similar_content = content_extractor(similar_chunks)

    return similar_content

def semantic_search(state: BotState):
    question = state["messages"]

    # get the most similar context
    similar_context = get_similar_context(question)

    return {"context": [similar_context]}


def answer_generator(state: BotState, config: RunnableConfig):
    searched_context = state["context"]
    messages = state["messages"]

    # generate the prompt as a system message
    system_message_prompt = [SystemMessage(ANSWER_INSTRUCTIONS.format(context = searched_context))]
    # invoke the llm
    answer = llm.invoke(system_message_prompt + messages, config)

    return {"answer": answer}

# add nodes and edges
helper_builder = StateGraph(BotState)
helper_builder.add_node("pinecone_retriever", semantic_search)
helper_builder.add_node("answer_generator", answer_generator)

# build graph
helper_builder.add_edge(START, "pinecone_retriever")
helper_builder.add_edge("pinecone_retriever", "answer_generator")
helper_builder.add_edge("answer_generator", END)

# compile the graph
helper_graph = helper_builder.compile()

async def graph_streamer(question_messages: list):
    # configurations
    node_to_stream = 'answer_generator'
    model_config = {"configurable": {"thread_id": "1"}}
    #input_message = HumanMessage(content=question)
    # streaming tokens
    async for event in helper_graph.astream_events({"messages": question_messages}, model_config, version="v2"):
        # Get chat model tokens from a particular node
        #print(event)
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node','') == node_to_stream:
            data = event["data"]
            yield data["chunk"].content