"""
Structure of the category/grader agent - grading company on the rubric of each category
"""

import json
import ast
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.constants import Send
from src.agent.state import State
from src.agent.rubric import COMPANY_RUBRIC, MICROSOFT_TEST_RUBRIC, PERSON_RUBRIC
import re

llm = ChatOpenAI(model="gpt-4o")
llm_json = ChatOpenAI(
    model="gpt-4o", model_kwargs={"response_format": {"type": "json_object"}}
)

query_collector = []

# ==============================================
# Constants Section
# ==============================================

MAX_REFLECTION_RETRY = 1
TESTING_MODE = True


# ==============================================
# Helper Functions
# ==============================================


def preprocess_json(value: str):
    cleaned_output = value.strip()
    cleaned_output = re.sub(r"^```|```$", "", cleaned_output).strip()
    if cleaned_output.startswith("json\n"):
        cleaned_output = cleaned_output[5:]
    return cleaned_output


# ==============================================
# Nodes Section
# ==============================================


def init_state(state: State):
    return {
        "messages": [SystemMessage(content=state["messages"][0]["content"])],
        "candidate_type": None,
        "current_candidate": None,
        "company_rubric": {
            "company_mission_alignment": None,
            "relevant_events": None,
            "sponsorship_history": None,
            "geographic_relevance": None,
        },
        "person_rubric": {
            "expertise_alignment": None,
            "company_relevance": None,
            "geographic_relevance": None,
        },
        "candidate_list": [],
        "main_iteration": 0,
        "current_category": None,
        "current_rubric": None,
        "reflection_iteration": 0,
    }


def query_keyword_agent(state: State):
    # TODO connection to the keyword agent

    """result = llm.invoke("Give a random list of 5 companies and 5 person names. In the format json [[\"microsoft\", \"company\"], [\"John\", \"person\"]]")
    result = result.content
    candidates = [item.strip() for item in result.split(",")]"""

    candidates = [("microsoft", "company")]
    return {**state, "candidate_list": candidates}


def candidate_processor(state: State):
    """This node checks if there is a candidate in state, if not, it queries the query_keyword_agent, if yes, it puts the candidate into a state"""

    sys_msg = ""  # defining the message that is going to append to the message state

    if len(state["candidate_list"]) == 0:
        sys_msg = "query_keyword_agent"  # outputs the conditional to go to keyword node to get the company

        return {
            **state,
            "messages": state["messages"] + [SystemMessage(content=sys_msg)],
            "main_iteration": state["main_iteration"] + 1,
        }

    else:  # takes the first candidate from the list and puts it into state
        candidate = state["candidate_list"][0]
        return {
            **state,
            "messages": state["messages"] + [SystemMessage(content="Candidate Chosen")],
            "candidate_type": candidate[1],
            "current_candidate": candidate[0],
            "candidate_list": state["candidate_list"][1:],
        }


def category_divider(state: State):  # TODO Need better name
    # Chooses candidate categories

    return state


    """ if state["candidate_type"] == "speaker":

        # loops through each category, if the category has not been marked, put the category into state and begin the marking process
        for category in PERSON_RUBRIC.keys():
            if (
                state["person_rubric"][category] == None
                or state["person_rubric"][category] == 0
            ):
                msg = f"Selected category {category}. Will begin marking now."
                current_rubric = PERSON_RUBRIC[category]
                return {
                    **state,
                    "messages": state["messages"][:1] + [SystemMessage(content=msg)],
                    "current_category": category,
                    "current_rubric": current_rubric,
                }

        # grading is complete all categories are marked.
        return {
            **state,
            "messages": state["messages"] + [SystemMessage(content="grading_complete")],
        }


    # Parallel Workflow
    elif state["candidate_type"] == "company":
        return [Send("rubric_reasoning_agent", {
                    **state,
                    "messages": state["messages"][:1] + [SystemMessage(content=msg)],
                    "current_category": category,
                    "current_rubric": COMPANY_RUBRIC[category],
                }) for category in COMPANY_RUBRIC.keys()]         

    # candidate did not have an identifier
    else:
        raise Exception("Error in identifying speaker or company!") """


def add_score_database(state: State):
    # TODO this is the node that adds the scores into the database and resets the state
    prompt = f"""
    You are an agent at the end of the workflow that is responsible for making the final say, yes or no to reaching out to the current candidate.
    Here are the previous messages: 
    """
    prompt = prompt + ", ".join(str(item.content) for item in state["messages"])

    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])
    return {**state, "messages": state["messages"] + [output]}


def rubric_reasoning_agent(state: State):
    prompt = f"""
    *Context*
    You are an analytical agent responsible for reasoning what information is needed to evaluate this rubric for deciding if this 
    entity suitable for sponsorship/partnership of our event {state["messages"][0].content}. 

    *Task*
    -  Break down each category of the rubric to identify what information is needed to fully assess a candidate against it 
    -  Consider the purpose of the criteria, the types of data or evidence required, and how these elements contribute to an informed decision
    - Provide a clear text of your reasoning process

    *Information*
    Here are useful information 
    - The entity name is {state['current_candidate']}
    - Entity is a {state['candidate_type']}

    *Rubric Category*
    Here is the rubric category you will be reasoning with. 
    {state["current_rubric"]}
    """

    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])

    return {**state, "messages": state["messages"] + [output]}


def generate_queries_agent(state: State):
    prompt = """
        *Context*
        You are a search agent responsible for crafting concise natural language queries retrieve relevant information within a vector database.

        *Task*
        - Reviewing the previous messages
        - Generate queries tailored to the rubric criteria and other previous messages that includes reasoning

        *Query Criteria*
        Here are the criteria that each query must meet:
        - Queries should the entity name
        - Do not include a time period

        *Output Format*
        - Output as JSON, following the format below:
        {
            query: string[]
        }
        
        *Previous Messages*
        
    """

    if TESTING_MODE:
        return state  # skip this node if testing mode is on

    prompt = prompt + ", ".join(
        str(item.content) for item in state["messages"]
    )  # will need to turn this to a string format TODO

    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])

    return {**state, "messages": state["messages"] + [output]}


def query_vector_db(state: State):

    # TODO connect the endpoint for database

    queries = state["messages"][-1].content.split(",")

    if TESTING_MODE:
        results = "\n".join(
            f"{title}: {desc}"
            for title, desc in MICROSOFT_TEST_RUBRIC[state["current_category"]]
        )
    else:
        pass  # TODO

    vector_output = AIMessage(content=results)

    return {**state, "messages": state["messages"] + [vector_output]}


def score_ranking_agent(state: State):
    prompt = f"""
    *Context*
    You are a grading agent responsible for using previous searched information and previous reasoning choose a score onto the rubric.  
    Goal is to determine whether entity suitable for sponsorship/partnership of our event {state["messages"][0].content}. 

    *Task*
    1. Understand the previous search results and rubric reasoning by reading previous messages attached below. 
    2. Use this understanding to **find the most reasonable score**.
    3. YOU MUST Provide the ranking in **JSON format** as described:
        - The score (as an int).
        - A concise but informative explanation for why the score holds this rank. Provide examples and evidence to back your score up.
        
    *Rubric*
    This is the official rubric: 
    ({state['current_category']}) 
   
    
    Previous messages on reasoning and search history:
    """

    prompt = prompt + ", ".join(
        str(item.content) for item in state["messages"]
    )  # TODO need a better way to store previous information rather than giving a bunch of messages.

    # Structured JSON output schema for the model
    schema = {
        "title": "Schema",
        "description": "A schema for storing chosen score and detailed concise reasoning",
        "type": "object",
        "properties": {
            "score": {"type": "integer", "minimum": 1, "maximum": 5},
            "reason": {
                "type": "string",
                "description": "The reason why you made this decision. Be concise but detailed with evidence and examples.",
            },
        },
        "required": ["score", "reason"],
    }

    llm_with_schema = llm_json.with_structured_output(schema=schema)

    sys_msg = SystemMessage(content=prompt)
    output = llm_with_schema.invoke([sys_msg])

    return {**state, "messages": state["messages"] + [AIMessage(str(output))]}


def reflection_agent(state: State):

    # Generating the prompt for the llm
    prompt = """
    You are a reflection within a workflow that is responsible for grading companies or people based on a certain rubric. 
    The previous agents have reasoned through the rubric and ranked the results by most likely to least likely score. Your task is to see reflect and double check if there is any error of thoughts within the workflow. 
    It is also important to not to be excessive and mark it as good if information is sufficient to rank these candidates. 
    
    1. Double check if we have enough information to make informed guesses. 
    2. Double check if there was any logic flaw in our reasoning.
    3. Output the next steps in the format given. You must strictly follow the provided JSON schema in your response. complete means the research and logic justifies the current grading. research_issue means we need more research. logic_flow_issue means our reasoning might have been flawed or forgot to consider a key factor. 
    
    
    Previous messages:\n  
    """
    prompt = prompt + ", ".join(str(item.content) for item in state["messages"])

    # Structured JSON output schema for the model
    schema = {
        "title": "Schema",
        "description": "A schema for deciding the next step and providing reasoning.",
        "type": "object",
        "properties": {
            "next_step": {
                "type": "string",
                "enum": ["complete", "research_issue", "logic_flow_issue"],
            },
            "reason": {
                "type": "string",
                "description": "The reason why you made this decision. Be concise but detailed.",
            },
        },
        "required": ["next_step", "reason"],
    }
    llm_with_schema = llm_json.with_structured_output(schema=schema)

    sys_msg = SystemMessage(content=prompt)
    output = llm_with_schema.invoke([sys_msg])
    # store the chosen score into the state if reasoning + research is good OR if over max iteration
    if (
        output["next_step"] == "complete"
        or state["reflection_iteration"] > MAX_REFLECTION_RETRY
    ):
        # resets the reflection iteration
        state["reflection_iteration"] = 0
        output["next_step"] = "complete"

        # Turns string representation of dict into a dict obj
        cleaned_output = ast.literal_eval(state["messages"][-1].content)

        if state["candidate_type"] == "person":
            return {
                **state,
                "messages": state["messages"] + [AIMessage(str(output))],
                "person_rubric": {
                    **state["person_rubric"],
                    state["current_category"]: (
                        int(cleaned_output["score"]),
                        str(cleaned_output["reason"]),
                    ),
                },
            }
        elif state["candidate_type"] == "company":
            return {
                **state,
                "messages": state["messages"] + [AIMessage(str(output))],
                "company_rubric": {
                    **state["company_rubric"],
                    state["current_category"]: (
                        int(cleaned_output["score"]),
                        str(cleaned_output["reason"]),
                    ),
                },
            }
    else:
        return {
            **state,
            "messages": state["messages"] + [AIMessage(str(output))],
            "reflection_iteration": state["reflection_iteration"] + 1,
        }



def aggregate_subgraph(state: State):
    pass
# ==============================================
# Conditional Function Section
# ==============================================


def candidate_processor_conditional(state: State):
    output = state["messages"][-1].content
    if output == "query_keyword_agent":
        return "query_keyword_agent"
    elif output == "END":
        return END
    else:
        return "category_divider"


def reflection_agent_conditional(state: State):
    output = ast.literal_eval(preprocess_json(state["messages"][-1].content))
    decision = output["next_step"]
    if decision == "complete":
        return END
    elif decision == "research_issue":
        return "query_vector_db"
    elif decision == "logic_flow_issue":
        return "score_ranking_agent"
    else:
        raise Exception()


def parallel_grading(state: State):
    # TODO add speaker
    
    if state["candidate_type"] == "company":
        return [Send("category_grading_subgraph", {
                    **state,
                    "messages": state["messages"][:1] + [SystemMessage(content=f"Selected category {category}. Will begin marking now.")],
                    "current_category": category,
                    "current_rubric": COMPANY_RUBRIC[category],
                }) for category in COMPANY_RUBRIC.keys()]         


# ==============================================
# Reasoning Subgraph Section
# ==============================================

category_grading_subgraph = StateGraph(State)

category_grading_subgraph.add_node("rubric_reasoning_agent", rubric_reasoning_agent)
category_grading_subgraph.add_node("generate_queries_agent", generate_queries_agent)
category_grading_subgraph.add_node("query_vector_db", query_vector_db)
category_grading_subgraph.add_node("score_ranking_agent", score_ranking_agent)
category_grading_subgraph.add_node("reflection_agent", reflection_agent)


category_grading_subgraph.add_conditional_edges(
    "reflection_agent",
    reflection_agent_conditional,
    {
        END: END,
        "query_vector_db": "query_vector_db",
        "score_ranking_agent": "score_ranking_agent",
    },
)

category_grading_subgraph.add_edge(START, "rubric_reasoning_agent")
category_grading_subgraph.add_edge("rubric_reasoning_agent", "generate_queries_agent")
category_grading_subgraph.add_edge("generate_queries_agent", "query_vector_db")
category_grading_subgraph.add_edge("query_vector_db", "score_ranking_agent")
category_grading_subgraph.add_edge("score_ranking_agent", "reflection_agent")


# ==============================================
# Mapping Nodes Section
# ==============================================


# Define the agent workflow graph
workflow = StateGraph(State)


# Add the node to the graph
workflow.add_node("init_state", init_state)
workflow.add_node("candidate_processor", candidate_processor)
workflow.add_node("query_keyword_agent", query_keyword_agent)
workflow.add_node("category_divider", category_divider)
workflow.add_node("category_grading_subgraph", category_grading_subgraph.compile())
workflow.add_node("add_score_database", add_score_database)


# Defining the architecture
workflow.add_edge(START, "init_state")
workflow.add_edge("init_state", "candidate_processor")
workflow.add_conditional_edges(
    "candidate_processor",
    candidate_processor_conditional,
    {
        END: END,
        "query_keyword_agent": "query_keyword_agent",
        "category_divider": "category_divider",
    },
)

workflow.add_conditional_edges(
    "category_divider",
    parallel_grading, ["category_grading_subgraph"]
)




workflow.add_edge("query_keyword_agent", "candidate_processor")
workflow.add_edge("category_grading_subgraph", "add_score_database")

# TMP TODO ending edge
workflow.add_edge("add_score_database", END)

# Compile the workflow into an executable graph
graph = workflow.compile()
# graph.invoke({
#     "messages": [],
#     "candidate_type": None,
#     "current_candidate": None,
#     "company_rubric": {
#         "company_mission_alignment": None,
#         "relevant_events": None,
#         "sponsorship_history": None,
#         "geographic_relevance": None,
#     },
#     "person_rubric": {
#         "expertise_alignment": None,
#         "company_relevance": None,
#         "geographic_relevance": None,
#     },
#     "candidate_list": [],
#     "main_iteration": 0,
#     "current_category": None,
#     "current_rubric": None,
# })
