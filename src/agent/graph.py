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
from src.agent.rubric import COMPANY_RUBRIC, SPEAKER_RUBRIC 

llm = ChatOpenAI(model="gpt-4o")

# ==============================================
# Nodes Section
# ==============================================

def query_keyword_agent(state: State):
    result = llm.invoke("Give a random list of 10 tech comapanies and return strictly only list of just names seperated by commas. No other text")
    result = result.content 
    candidates = [item.strip() for item in result.split(",")]
    return {**state, "candidate_list": candidates}


def candidate_processor(state: State):
    
    # recieves the candidates list
    candidates = ", ".join(state["candidate_list"])
    sys_msg = ""

    
    if (len(state["candidate_list"]) == 0):
        if (state["main_iteration"] > 3): # TODO rename variable
            sys_msg = "END"
        else: 
            sys_msg = "query_list_company"
        
        return {**state, "messages": state["messages"] + [SystemMessage(content=sys_msg)], "main_iteration": state["main_iteration"] + 1}
    else:
        candidate = state["candidate_list"][0]
        prompt = f""" # part of the meta data
                    There are candidates in the list. The candidate is {candidate}. 
                    1. Identify whelther this candidate is a "company" or a "speaker" then output in this in JSON format. Below are examples you must follow. Output only JSON without any additional text.
                    candidate_type must be either "company" or "speaker" and candidate_name must be {candidate}
                    
                    Example:
                    {{ "candidate_name": "Microsoft", "candidate_type": "company"}}
                    Example 2:
                    {{"candidate_name": "John Doe", "candidate_type": "speaker"}}
                    
                    """

        sys_msg = SystemMessage(content=prompt)
        output = llm.invoke([sys_msg] + state["messages"])
        data = None
        try: 
            data = json.loads(output.content)
        except json.JSONDecodeError as e:
            return {**state, "messages": state["messages"] + [SystemMessage(content="END")]}
        return {**state, "messages": state["messages"] + [SystemMessage(content="Candidate Chosen")],"candidate_type": data["candidate_type"], "current_candidate": state["candidate_list"][0], "candidate_list": state["candidate_list"][1:]}


def category_divider(state: State):
    if (state["candidate_type"] == "speaker"):
        for category in SPEAKER_RUBRIC.keys():
            if (state["speaker_rubric"][category] == None or state["speaker_rubric"][category] == 0):
                msg = f"Selected category {category}. Will begin marking now."
                current_rubric = SPEAKER_RUBRIC[category]
                return {**state, "messages": state["messages"] + [SystemMessage(content=msg)], "current_category": category, "current_rubric": current_rubric}
        return {**state, "messages": state["messages"] + [SystemMessage(content="grading_complete")]}
    
    elif (state["candidate_type"] == "company"):
        for category in COMPANY_RUBRIC.keys():
            if (state["company_rubric"][category] == None or state["company_rubric"][category] == 0):
                msg = f"Selected category {category}. Will begin marking now."
                current_rubric = COMPANY_RUBRIC[category]
                return {**state, "messages": state["messages"] + [SystemMessage(content=msg)], "current_category": category, "current_rubric": current_rubric}
            
        return {**state, "messages": state["messages"] + [SystemMessage(content="grading_complete")]}
    else:
        raise Exception("Error in identifying speaker or company!")

def add_score_database(state: State):
    # TODO this is the node that adds the scores into the database and resets the state
    return state

def rubric_reasoning_agent(state: State):
    prompt = """
    You are an analytical agent tasked with evaluating a candidate's suitability for sponsorship/partnership using the rubric provided. 
    Carefully read and interpret the rubric to understand its criteria and intent.
    Break down each category of the rubric to identify what specific information is needed to fully assess a candidate against it. 
    Consider the underlying purpose of each criterion, the types of data or evidence required, and how these elements contribute to an informed decision.
    Provide a clear text of your reasoning process. \n
    Here is the rubric category:
    """
    prompt = prompt + state["current_rubric"]
    
    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])
    
        
    return {**state, "messages": state["messages"] + [output]}


# ==============================================
# Conditional Function Section
# ==============================================

def candidate_processor_conditional(state: State):
    output = state["messages"][-1].content
    if (output == "query_list_company"):
        return "query_keyword_agent"
    elif (output == "END"):
        return END
    else:
        return "category_divider" 
    
    
def category_divider_conditional(state: State):
    output = state["messages"][-1].content
    if (output == "grading_complete"):
        return "add_score_database" # TODO (this has to go towards a node that stores it into the database)
    else:
        return "rubric_reasoning_agent" # TODO






# ==============================================
# Mapping Nodes Section
# ==============================================


# Define the agent workflow graph
workflow = StateGraph(State)


# Add the node to the graph
workflow.add_node("candidate_processor", candidate_processor)
workflow.add_node("query_keyword_agent", query_keyword_agent)
workflow.add_node("category_divider", category_divider)
workflow.add_node("add_score_database", add_score_database)
workflow.add_node("rubric_reasoning_agent", rubric_reasoning_agent)


# Defining the architecture 
workflow.add_edge(START, "candidate_processor")
workflow.add_conditional_edges(
    "candidate_processor",
    candidate_processor_conditional,
    {END: END, "query_keyword_agent": "query_keyword_agent", "category_divider": "category_divider"}
)

workflow.add_conditional_edges(
    "category_divider",
    category_divider_conditional,
    {"add_score_database": "add_score_database", "rubric_reasoning_agent": "rubric_reasoning_agent"}
)

workflow.add_edge("query_keyword_agent", "candidate_processor")
workflow.add_edge("rubric_reasoning_agent", END)


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