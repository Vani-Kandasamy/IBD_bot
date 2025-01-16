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

import base64
import os
import streamlit as st

os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"]= st.secrets["PINECONE_API_KEY"]
os.environ["INDEX_HOST"]= st.secrets["INDEX_HOST"]

NAMESPACE_KEY = "Keya"
TEXT_MODEL = "text-embedding-ada-002"

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(host=os.environ["INDEX_HOST"])
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# to check user query greeting or not
class GreetingTester(BaseModel):
    greeting: bool = Field(None, description = "Greeting or Not")

# this is be default has the messages and add_messages reducers
class BotState(MessagesState):
    image_path: str
    context: Annotated[list, operator.add]
    answer: str
    accept_content: bool
    image_description: str

class ImageDescription(BaseModel):
    description: str = Field(None, description = "Description of the image")
    proper_content: bool = Field(None, description = "True if the image is about IBS disease else False")

# will answer given context
ANSWER_INSTRUCTIONS = """ You are an expert nutritionist for IBD patients.

You are an expert being explained based on given information.

You goal is to explain more about the given information precisely based on the context.

To explain, use this context:

{context}

When explaining, follow these guidelines:

1. Use only the information provided in the context.

2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
"""

# does not provide context
IMAGE_INSTRUCTIONS = """You are an expert nutritionist for IBD patients.

You are an expert generating descriptions based on given image.

When generating descriptions for images, follow these guidelines:

1. Use only the information provided in the image.

2. If the image is not about IBS disease, Mention image is not about IBS.
"""

# will provide response only based on image input context
GUIDANCE_INSTRUCTIONS = """You are an expert nutritionist for IBD disease.

Please follow these guidelines below to provide user guidance.

Please mention that you are only trained to given explanation about IBS disease related images.

{context}

1. Analyze the given context.

2. If they are about IBS disease, please proivde useful guidance upload images about IBS disease related images.

"""

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

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

# retrieve content from Pinecone
def semantic_search(state: BotState):
    question = state["messages"]

    # get the most similar context
    similar_context = get_similar_context(question)
    print(similar_context)
    return {"context": [similar_context]}

def answer_generator(state: BotState, config: RunnableConfig):
    searched_context = state["context"]
    image_description = state["image_description"]

    # generate the prompt as a system message
    system_message_prompt = [SystemMessage(ANSWER_INSTRUCTIONS.format(context = searched_context))]
    # messages
    human_messages = [HumanMessage(content = f"Please explain more about these: {image_description}")]
    # invoke the llm
    answer = llm.invoke(system_message_prompt + human_messages, config)

    return {"answer": answer}

def image_description_generator(state: BotState):
    image_local_path = state["image_path"]
    image_data = encode_image(image_local_path)
    # set up the message
    message = HumanMessage(
        content=[
            {"type": "text", "text": IMAGE_INSTRUCTIONS},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            },
        ],
    )
    # create a structured output
    structured_llm = llm.with_structured_output(ImageDescription)
    # invoke the llm to generatr an query
    invoke_image_query = structured_llm.invoke([message])

    return {"accept_content": invoke_image_query.proper_content, "image_description": invoke_image_query.description}

def user_guider(state: BotState, config: RunnableConfig):
    image_description = state["image_description"]

    # invoke the llm
    invoke_image_query = llm.invoke([SystemMessage(content=GUIDANCE_INSTRUCTIONS.format(context = image_description))], config)

    return {"answer":invoke_image_query }

def conditional_checker(state: BotState):
    content_status = state["accept_content"]

    if content_status:
        return "pinecone_retriever"

    return "guidelines_generator"

# add nodes and edges
helper_builder = StateGraph(BotState)
helper_builder.add_node("description_generator", image_description_generator)
helper_builder.add_node("pinecone_retriever", semantic_search)
helper_builder.add_node("answer_generator", answer_generator)
helper_builder.add_node("guidelines_generator", user_guider)

# build graph
helper_builder.add_edge(START, "description_generator")
helper_builder.add_conditional_edges("description_generator", conditional_checker, ["pinecone_retriever", "guidelines_generator"])
helper_builder.add_edge("guidelines_generator", END)
helper_builder.add_edge("pinecone_retriever", "answer_generator")
helper_builder.add_edge("answer_generator", END)

# compile the graph
helper_graph = helper_builder.compile()

async def graph_streamer(path: str):
    node_to_stream = 'answer_generator'
    other_node_to_stream = 'guidelines_generator'
    model_config = {"configurable": {"thread_id": "1"}}

    async for event in helper_graph.astream_events({"image_path": path}, model_config, version="v2"):
        # Get chat model tokens from a particular node

        if event["event"] == "on_chat_model_stream":
            if event['metadata'].get('langgraph_node','') == node_to_stream or  event['metadata'].get('langgraph_node','') == other_node_to_stream:
                data = event["data"]
                yield data["chunk"].content