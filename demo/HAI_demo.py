import streamlit as st
import streamlit_mermaid as stmd

import utils
from openai import OpenAI
import agents

# Add OpenAI API key input in sidebar
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None
if "api_key_validated" not in st.session_state:
    st.session_state.api_key_validated = False

api_key = st.sidebar.text_input(
    "OpenAI API key",
    type="password",
    value=(st.session_state.openai_api_key if st.session_state.openai_api_key else ""),
)
validate_button = st.sidebar.button("Validate Key", key="validate_api_key")

if validate_button:
    if api_key:
        try:
            # Test the API key with a simple request
            client = OpenAI(api_key=api_key)
            client.models.list()  # This will raise an error if the key is invalid
            st.session_state.openai_api_key = api_key
            st.session_state.api_key_validated = True
            st.sidebar.success("API key validated successfully!")

        except Exception as e:
            st.sidebar.error("Invalid API key. Please check and try again.")
            st.session_state.openai_api_key = None
            st.session_state.api_key_validated = False
    else:
        st.sidebar.warning("Please enter an API key to validate.")
        st.session_state.api_key_validated = False

if not st.session_state.api_key_validated:
    st.sidebar.warning(
        "Please enter and validate your OpenAI API key to use the chat features."
    )

# Add sidebar selection
view_mode = st.sidebar.selectbox(
    "Select View", ["Live Chat", "Pre-loaded Conversation",]
)

model = "gpt-4.1"

st.title("Interactive Chat-Based Task Planner")

if view_mode == "Live Chat":
    if not st.session_state.api_key_validated:
        st.error(
            "Please enter and validate your OpenAI API key in the sidebar to use the live chat."
        )
    else:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        # Initialize chat history
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        for message in st.session_state.conversation_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Enter your message:")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            # Add user message to chat history
            st.session_state.conversation_history.append(
                {"role": "user", "content": user_input}
            )


            with st.chat_message("assistant"):
                
                rewritten_intent = agents.intent_rewriter(client, model, user_input)
                plan = agents.planner(client, model, rewritten_intent)

                st.info(f"**User Intent**: {rewritten_intent}")
                st.info("**Generated Plan**")
                stmd.st_mermaid(utils.generate_mermaid(plan))
                

                response = agents.openai_dialogue_agent(
                client, model, st.session_state.conversation_history, rewritten_intent, plan)
                st.write(response)
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": response}
                )

else:
    if not st.session_state.openai_api_key:
        st.error("Please enter a valid OpenAI API key in the sidebar to view plans.")
    else:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        # Pre-defined conversations
        predefined_conversations = {
            "Job Search": [
                "user: I need help finding a job in software engineering",
                "assistant: I can help you with your job search. What's your experience level and preferred location?",
                "user: I have 3 years of experience and I'm open to remote work",
                "assistant: Great! Let me outline a plan for your job search strategy.",
            ],
            "Travel Planning": [
                "user: I want to plan a trip to Europe",
                "assistant: I'll help you plan your European trip. When are you planning to go and for how long?",
                "user: I'm thinking about 2 weeks in summer",
                "assistant: Perfect! Let me create a travel planning strategy for you.",
            ],
            "Learning New Skill": [
                "user: I want to learn Python programming",
                "assistant: I can help you create a learning plan for Python. Do you have any programming experience?",
                "user: I'm a complete beginner",
                "assistant: No problem! Let me outline a structured learning path for you.",
            ],
        }
        st.write("Compare the impact of effective user intent understanding on planning.")
        selected_conversation = st.selectbox(
            "Select a Pre-loaded Conversation", list(predefined_conversations.keys())
        )

        # Display the selected conversation
        st.write("**Selected Conversation:**")
        for message in predefined_conversations[selected_conversation]:
            role, content = message.split(": ", 1)
            with st.chat_message(role):
                st.markdown(content)

        with st.chat_message("assistant"):
            st.write("Generated Plans:")
            col1, col2 = st.columns(2)
            with col1:
                rewritten_intent = agents.intent_rewriter(
                    client, model, predefined_conversations[selected_conversation]
                )
                st.info(f"Planned using the intent:\n {rewritten_intent}")
                
                plan = agents.planner(client, model, rewritten_intent)
                markdown = utils.generate_mermaid(plan)
                stmd.st_mermaid(markdown)
            with col2:
                st.info("Planned using the entire conversation.")
                plan = agents.planner(
                    client, model, predefined_conversations[selected_conversation]
                )
                markdown = utils.generate_mermaid(plan)
                stmd.st_mermaid(markdown)
