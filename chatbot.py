import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms.sagemaker_endpoint import LLMContentHandler, SagemakerEndpoint
from typing import Dict
import json
from io import StringIO
from random import randint

st.set_page_config(page_title="Document Analysis", page_icon=":robot:")
st.header("Chat with your document 📄  (Model: Falcon-40B-Instruct)")

endpoint_name = "falcon-40b-instruct-2023-06-08-06-42-03-876"


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"
    len_prompt = 0

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        self.len_prompt = len(prompt)
        input_str = json.dumps({"inputs": prompt, "parameters": {"max_new_tokens": 100, "stop": ["Human:"], "do_sample": False, "repetition_penalty": 1.1}})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = output.read()
        res = json.loads(response_json)
        ans = res[0]['generated_text'][self.len_prompt:]
        ans = ans[:ans.rfind("Human")].strip()
        return ans


content_handler = ContentHandler()


@st.cache_resource
def load_chain():
    llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        region_name="us-east-1",
        content_handler=content_handler,
    )
    memory = ConversationBufferMemory()
    chain = ConversationChain(llm=llm, memory=memory)
    return chain

# this is the object we will work with in the ap - it contains the LLM info as well as the memory
chatchain = load_chain()

# initialise session variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
    chatchain.memory.clear()
if 'widget_key' not in st.session_state:
    st.session_state['widget_key'] = str(randint(1000, 100000000))

# Sidebar - the clear button is will flush the memory of the conversation
st.sidebar.title("Sidebar")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['widget_key'] = str(randint(1000, 100000000))
    chatchain.memory.clear()

# upload file button
uploaded_file = st.sidebar.file_uploader("Upload a txt file", type=["txt"], key=st.session_state['widget_key'])

# this is the container that displays the past conversation
response_container = st.container()
# this is the container with the input text box
container = st.container()

with container:
    # define the input text box
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    # when the submit button is pressed we send the user query to the chatchain object and save the chat history
    if submit_button and user_input:
        output = chatchain(user_input)["response"]
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
    # when a file is uploaded we also send the content to the chatchain object and ask for confirmation
    elif uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        content = stringio.read()
        content += "\nPlease confirm that you have read that file by saying 'Yes, I have read the file'"
        output = chatchain(content)["response"]
        st.session_state['past'].append("I have uploaded a file. Please confirm that you have read that file.")
        st.session_state['generated'].append(output)

# this loop is responsible for displaying the chat history
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
