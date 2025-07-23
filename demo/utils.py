import ast


# Function to generate Mermaid diagram
def escape_char(s: str) -> str:
    """
    Convert any non-alphabetic and non-digit characters in a string
    into their corresponding HTML entity codes.

    :param s: The input string
    :return: The converted string with special characters replaced by HTML entities
    """
    return "".join(
        c if c.isalnum() or c in [" ", ",", "."] else f"#{ord(c)};" for c in s
    )
    return 


def generate_mermaid(plan_str):
    if isinstance(plan_str, str):
        plan = ast.literal_eval(plan_str)
    else:
        plan = plan_str
    nodes, edges = plan["nodes"], plan["edges"]
    node_name = {item["id"]: item["name"] for item in nodes}

    content = "\n".join(
        [f"{s}[\"{s}{node_name[s]}\"]-->{e}[\"{e}{node_name[e]}\"]" for (s, e) in edges]
    )
    markdown = "graph TD\n" + content + "\n"
    print("MERMAID RESPONSE: ", markdown)
    return markdown
