"""
Structure of the category/grader agent - grading company on the rubric of each category
"""


import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState 
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.tools import tool
from src.agent.state import State




# Tool
@tool
def query_list_company(message: str):
    """Querys the vector db. The arguments accepted in message str is ONLY company or search_company

    Args:
        message: keyword on what the event is about 
    """
    
    return llm.invoke("Give a random list of 10 tech comapanies and return strictly only JSON with the list of just names. No other text")



llm = ChatOpenAI(model="gpt-4o")
supervisor_agent = llm.bind_tools([query_list_company])


def query_list_node(state: State):
    result = llm.invoke("Give a random list of 10 tech comapanies and return strictly only list of just names seperated by commas. No other text")
    result = result.content 
    candidates = [item.strip() for item in result.split(",")]
    return {**state, "candidate_list": candidates}


def supervisor_agent_node(state: State):
    
    # recieves the candidates list
    candidates = ", ".join(state["candidate_list"])
    
    prompt = """"You part of a grading assistant. You're are solely responsible for identifying if there is any candidates left to grade. If there is, you output json.
                Follow this structured process to reason through the next step:
                """

    
    if (len(state["candidate_list"]) == 0):
        prompt_empty = """
                There is currently no companies in your state. You are given these two options: Please output one of the two outputs 
                 
                 1. Prompt the tool of querying a new list companies. Output query_list_company without quotation marks and additional text.
                 2. After one iteration of query_list_company call, go to end node. Output END without quotation marks and additional text.
                 
                You MUST only output the given outputs Literal[query_list_company, END].
        """

        prompt = prompt + prompt_empty
    else:
        candidate = state["candidate_list"][0]
        
        prompt_non_empty = f"""
                    There are candidates in the list. The candidate is {candidate}. 
                    1. Identify whelther this candidate is a "company" or a "speaker" then output in this in JSON format. Below are examples you must follow. Output only JSON without any additional text.
                    candidate_type must be either "company" or "speaker" and candidate_name must be {candidate}
                    
                    Example:
                    {{ "candidate_name": "Microsoft", "candidate_type": "company"}}
                    Example 2:
                    {{"candidate_name": "John Doe", "candidate_type": "speaker"}}
                    
                    """
        prompt = prompt + prompt_non_empty
        
    
    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg] + state["messages"])
    print(output)
    print("\n")
    return {**state, "messages": state["messages"] + [AIMessage(content=output.content)]}


def planner_agent_node(state: State):
    data = {}
    try: 
        data = json.loads(state["messages"][-1].content)
    except json.JSONDecodeError as e:
        pass # TODO
    
    return {**state, "candidate_type": data["candidate_type"], "current_candidate": state["candidate_list"][0], "candidate_list": state["candidate_list"][1:]}

def supervisor_agent_condition(state: State):
    output = state["messages"][-1].content
    if (output == "query_list_company"):
        return "query_list_node"
    elif (output == "END"):
        return END
    else:
        try: 
            data = json.loads(output)
        except json.JSONDecodeError as e:
            return END
        return "planner_agent_node" # TODO this is supposed to be the next node


# tools that the agent has access to
tools = [query_list_company]

# Define the agent workflow graph
workflow = StateGraph(State)

# Add the node to the graph
workflow.add_node("supervisor_agent_node", supervisor_agent_node)
workflow.add_node("query_list_node", query_list_node)
workflow.add_node("planner_agent_node", planner_agent_node)

# Defining the architecture 
workflow.add_edge(START, "supervisor_agent_node")
workflow.add_conditional_edges(
    "supervisor_agent_node",
    supervisor_agent_condition,
    {END: END, "query_list_node": "query_list_node", "planner_agent_node": "planner_agent_node"}
)
workflow.add_edge("query_list_node", "supervisor_agent_node")
workflow.add_edge("planner_agent_node", END)

# Compile the workflow into an executable graph
graph = workflow.compile()
# graph.invoke({
#         "messages": [],
#         "candidate_type": None,  
#         "current_candidate": None,  
#         "company_rubric": {
#             "company_mission_alignment": 1,
#             "relevant_events": 1,
#             "sponsorship_history": 1,
#             "geographic_relevance": 1,
#         },
#         "speaker_rubric": {
#             "speaker_expertise_alignment": 1,
#             "company_relevance": 1,
#             "geographic_relevance": 1,
#         },
#         "candidate_list": [],  
#     })