from openai import OpenAI
import streamlit as st
import json




def intent_rewriter(client, model, conversation_history):
    conversation = "\n".join(conversation_history)
    PLAN_WRITER_PROMPT = f"""Summarize the following USER-AGENT conversation into a single, concise sentence describing the user’s intended task 
        The summary should reflect the user’s goal or intent, in an instruction style. Do not introduce new information. Only include what is stated or clearly implied.
        The intent should reflect the latest intent and can include multiple intents. Ingore unrelated utterences. If later unterence is not directly related to uer intent, keep the previous intent.
        Example: 
        User: I want to learn about testing software
        Assistant: sure....
        User: How are you?
        Here intent should still be [learn about software testing]
        Conversation:
        {conversation}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": PLAN_WRITER_PROMPT}],
        stream=False,
        temperature=0,
    )
    print("INTENT REWRITER RESPONSE: ", response.choices[0].message.content)
    return response.choices[0].message.content


# Placeholder for planner module
def planner(client, model, request_str):

    if isinstance(request_str, list):
        request_str = "\n".join(request_str)
    PLAN_PROMPT = f"""
You are a planner responsible for creating high-level plans to solve any task. Understand the user intent from the input and plan accordingly. Consider breaking down complex tasks into subtasks.
Represent your plan as a graph where each node corresponds to a step, and each edge represents a dependency between two steps. A plan should have at least 2 steps.
If a node requires the output from a previous node as an input, ensure it is included in the edge list.
The output should be structured in the following JSON format:
'nodes': <list of JSON nodes with keys 'id': <node id as integer>, 'name': <sub-task node name>>,
'edges': <list of tuples [node_id, node_id]>

Input: {request_str}
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": PLAN_PROMPT}],
        stream=False,
        temperature=0,
    )
    response = response.choices[0].message.content
    print("PLANNER RESPONSE: ", response)
    if response.startswith("```json"):
        response = response.strip("```json\n").strip("```")
    return response





def openai_dialogue_agent(client, model, dialogue_history, intent, plan):
    if isinstance(dialogue_history, list):
        dialogue_history = "\n".join([str(ut) for ut in dialogue_history])
    DIALOGUE_PROMPT = """
        You are a response generation module in a dialogue agent. You will be given a conversation between a user and an assistant. Another module will analyze the user's intent and generate a plan to fulfill the user's request.

        Your task:
        * Continue the conversation based on the provided intent and plan, **be concise**
        * **Do not attempt** to create your own plan—rely solely on the given intent and plan.
        * Clearly explain how the plan would be executed if the system had access to real tools and data sources.
        * Since this is a demonstration, simulate the results of executing the plan and continue the conversation accordingly. **Clearly communicate** to the user that this is not real data.
        """
    content = f"Conversation:{dialogue_history}\n Intent:{intent} \n Plan:{json.dumps(plan)}  "
    
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DIALOGUE_PROMPT},
            {"role": "user", "content": content},
        ],
        stream=True,
        temperature=0,
    )
    return stream
