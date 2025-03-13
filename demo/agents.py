from openai import OpenAI
import streamlit as st





def intent_rewriter(client, model, conversation_history):
    conversation = "\n".join(conversation_history)
    PLAN_WRITER_PROMPT = f"""Your task is to transform a conversation between a USER and an AGENT into a clear and unambiguous 'task sentence' that includes all relevant information and reflects the user's intents as expressed throughout the conversation. 
Input: {conversation}
Your output should be phrased as an instructional sentence, such as "Build a ..." or "Design a ...".
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


def openai_dialogue_agent(client, model, dialogue_history):
    if isinstance(dialogue_history, list):
        dialogue_history = "\n".join([str(ut) for ut in dialogue_history])
    DIALOGUE_PROMPT = "Please continue the conversation with the user."
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DIALOGUE_PROMPT},
            {"role": "user", "content": dialogue_history},
        ],
        stream=True,
        temperature=0,
    )
    return stream
