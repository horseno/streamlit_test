import sys
from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="interactive demo")

st.title("Intention unwrapping demo")

CHOICES = {
    1: "gpt-4o",
    2: "Unwrap without system info",
    3: "Unwrap and align with system info",
    4: "interact and plan",
}


def format_func(option):
    return CHOICES[option]


add_selectbox = st.sidebar.selectbox("strategy",
                                     options=list(CHOICES.keys()),
                                     format_func=format_func)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

system_prompt1 = "You are a chat assistant, please interact with the user and ask clarification questions to fully understand their intention from the requests,\
                such that it can be converted into actionable steps in a compound AI system. \
                Please keep the questions concise with few options, and finally give a rephrased user request."

system_prompt2 = (
    system_prompt1 +
    """Return the request in the format Goal: <retrive or search, take actions, invoking external tools>,\
          Constraints: <any constraints to fullfil the task, like time, cost and accuracy>. \
          The request will later be fullfilled by the a system with the following agents:\
          Data source discovery agent: input is a keyword and output is a data source that contains coresponding information.\
          Data retriever agent: inputs are datasource and predicates, output is the retrieved information. 
          Retrieval task can vary significantly on execution time and number of results returned, ask user for time constraints.\
          External APIs: agents that can call external tools like check weather, data and time, or calculator.\
          Present agent: input contents and constraints, output correct presenation of the content. \
        The system has the following data sources available.
        Job posting table from Indeed (job title, company, city, job type ID, etc.)
        Company table from Indeed (company, HQ location, etc.)
        skills dataset
        Job type (e.g., fulltime) mapping table (job type ID, job type label)
        Wikipedia articles
            San Francisco Bay Area
            San Francisco
            Guangdong–Hong Kong–Macao Greater Bay Area (China)
            Tampa Bay area
""")

system_prompt_plan = (
    system_prompt2 +
    "Examine the request and identify a task plan  thatcan be fulfilled by various agents. Return both request and\
    Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:"
)

if add_selectbox == 1:
    system_prompt = "You are a helpful assistant"
elif add_selectbox == 2:
    system_prompt = system_prompt1
elif add_selectbox == 3:
    system_prompt = system_prompt2
elif add_selectbox == 4:
    system_prompt = system_prompt_plan

if prompt := st.chat_input("I'm looking for a job."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{
                "role": "system",
                "content": system_prompt
            }] + [{
                "role": m["role"],
                "content": m["content"]
            } for m in st.session_state.messages],
            stream=True,
            temperature=0,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
