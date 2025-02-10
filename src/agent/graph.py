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
from src.agent.state import State
from src.agent.rubric import COMPANY_RUBRIC, PERSON_RUBRIC 
import re

llm = ChatOpenAI(model="gpt-4o")
llm_json = ChatOpenAI(model="gpt-4o", model_kwargs={ "response_format": { "type": "json_object" } })


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
            "reflection_iteration": 0
        }



def query_keyword_agent(state: State):
    # TODO connection to the keyword agent
    
    
    """ result = llm.invoke("Give a random list of 5 companies and 5 person names. In the format json [[\"microsoft\", \"company\"], [\"John\", \"person\"]]")
    result = result.content 
    candidates = [item.strip() for item in result.split(",")] """
    

    candidates = [("microsoft", "company")]
    return {**state, "candidate_list": candidates}


def candidate_processor(state: State):
    """This node checks if there is a candidate in state, if not, it queries the query_keyword_agent, if yes, it puts the candidate into a state"""
    
    sys_msg = "" # defining the message that is going to append to the message state

    if (len(state["candidate_list"]) == 0):
        sys_msg = "query_keyword_agent" # outputs the conditional to go to keyword node to get the company
        
        return {**state, "messages": state["messages"] + [SystemMessage(content=sys_msg)], "main_iteration": state["main_iteration"] + 1} 
    
    else: # takes the first candidate from the list and puts it into state
        candidate = state["candidate_list"][0]
        return {**state, "messages": state["messages"] + [SystemMessage(content="Candidate Chosen")],"candidate_type": candidate[1], "current_candidate": candidate[0], "candidate_list": state["candidate_list"][1:]}


def category_divider(state: State): # TODO Need better name    
    # Chooses candidate categories

    if (state["candidate_type"] == "speaker"):
        
        # loops through each category, if the category has not been marked, put the category into state and begin the marking process 
        for category in PERSON_RUBRIC.keys():
            if (state["person_rubric"][category] == None or state["person_rubric"][category] == 0): 
                msg = f"Selected category {category}. Will begin marking now."
                current_rubric = PERSON_RUBRIC[category]
                return {**state, "messages": state["messages"][:1] + [SystemMessage(content=msg)], "current_category": category, "current_rubric": current_rubric}

        # grading is complete all categories are marked.
        return {**state, "messages": state["messages"] + [SystemMessage(content="grading_complete")]}
    
    # if candidate is company, we use the company_rubric
    elif (state["candidate_type"] == "company"):
        for category in COMPANY_RUBRIC.keys():
            if (state["company_rubric"][category] == None or state["company_rubric"][category] == 0):
                msg = f"Selected category {category}. Will begin marking now."
                current_rubric = COMPANY_RUBRIC[category]
                return {**state, "messages": state["messages"][:1] + [SystemMessage(content=msg)], "current_category": category, "current_rubric": current_rubric}
            
        return {**state, "messages": state["messages"] + [SystemMessage(content="grading_complete")]}
    
    # candidate did not have an identifier
    else:
        raise Exception("Error in identifying speaker or company!")

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
    You are an analytical agent tasked with evaluating a candidate's suitability for sponsorship/partnership using the rubric provided. 
    Carefully read and interpret the rubric to understand its criteria and intent.
    Break down each category of the rubric to identify what specific information is needed to fully assess a candidate against it. 
    Consider the underlying purpose of each criterion, the types of data or evidence required, and how these elements contribute to an informed decision.
    Provide a clear text of your reasoning process. Keep everything concise. The current candidate is {state['current_candidate']}. You are researching about a {state['candidate_type']} \n
    Here is the rubric category:
    """
    prompt = prompt + state["current_rubric"]
    
    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])
    
    return {**state, "messages": state["messages"] + [output]}


def generate_queries_agent(state: State): 
    prompt = """
    You are a search agent responsible for crafting precise and efficient search queries to retrieve the most relevant information. 
    Your goal is to support other agents in grading according to the rubric provided by generating high-quality search queries that maximize relevance and minimize the number of searches required.
    
    1. Understand the rubric by reviewing the previous messages, where earlier agents have analyzed and reasoned through the criteria to determine the necessary information.
    2. Generate 50 search queries tailored to the rubric criteria and other agent's reasoning
    3. Use the 50 queries to narrow it down to 5 queries by ensuring queries are specific enough to retrieve relevant results yet broad enough to minimize redundancy.
    4. ONLY output the 5 queries into each query seperated by commas. Example: query1, query2 
    
    Limit queries to 5. 
    
    Previous messages:\n  
    """
    
    for item in state["messages"]:
        print(item)
    
    prompt = prompt + ", ".join(str(item.content) for item in state["messages"]) # will need to turn this to a string format TODO 
    
    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])
    
    return {**state, "messages": state["messages"] + [output]}

def query_vector_db(state: State):
    
    # TODO connect the endpoint for database 
    
    queries = state["messages"][-1].content.split(",")
    
    print(queries)
    
    results = ""
    
    alternating = "negative"
    for query in queries:
        # alternating = "negative" if alternating == "positive" else "positive"
        results = results + "Query: " + query + "\nResults: " + llm.invoke(f"(instruction make this {alternating} paragraph about the topic) Generate a very short paragraph on this query about " + query).content + "\n"
        
    
    
    vector_output = AIMessage(content=results)
    
    return {**state, "messages": state["messages"] + [vector_output]}

def score_ranking_agent(state: State): 
    prompt = f"""
    You are a grading ranker agent responsible for using previous searched information and previous reasoning to rank each score choice on the rubric. 
    Output in order of top (most likley) to bottom (least likely) score with a short explanation. Output ONLY JSON with no additional TEXT. 
    
    1. Understand the previous search results and rubric reasoning by reading previous messages attached below. 
    2. Use this understanding to **rank scores from most likely to least likely**.
    3. Provide the ranking in **JSON format**, where each entry contains:
        - The score (as a string).
        - A concise but informative explanation for why the score holds this rank.
   
    Example output format: [["3", "explanation"], ["2", "explanation"], ["1", "explanation"]]
    
    Previous messages:\n  
    """ 
    
    prompt = prompt + ", ".join(str(item.content) for item in state["messages"]) # TODO need a better way to store previous information rather than giving a bunch of messages. 
    
    sys_msg = SystemMessage(content=prompt)
    output = llm.invoke([sys_msg])
    
    return {**state, "messages": state["messages"] + [output]}


def reflection_agent(state: State): 
    
    # Generating the prompt for the llm
    prompt = """
    You are a reflection within a workflow that is responsible for grading companies or people based on a certain rubric. 
    The previous agents have reasoned through the rubric and ranked the results by most likely to least likely score. Your task is to see reflect and double check if there is any error of thoughts within the workflow. 
    It is also important to not to be excessive and mark it as good if information is sufficient to rank these candidates. 
    
    1. Double check if we have enough information to make informed guesses. 
    2. Double check if there was any logic flaw in our reasoning.
    3. Output the next steps in the format given. You must output the format given in JSON. complete means the rearch and logic justifies the current grading. research_issue means we need more research. logic_flow_issue means our reasoning might have been flawed or forgot to consider a key factor. 
    
    
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
                    "enum": ["complete", "research_issue", "logic_flow_issue"]
                },
                "reason": {
                    "type": "string",
                    "description": "The reason why you made this decision. Be concise but detailed."
                }
            },
            "required": ["next_step", "reason"]
        }
    llm_with_schema = llm_json.with_structured_output(schema=schema)
    
    sys_msg = SystemMessage(content=prompt)
    output = llm_with_schema.invoke([sys_msg])
    
    # store the chosen score into the state if reasoning + research is good
    if output["next_step"] == "complete":
        
        # resets the reflection iteration
        state["reflection_iteration"] = 
        
        # TODO remove this once structured output implemented on the scoring agent
        cleaned_output = preprocess_json(state["messages"][-1].content)
        print(cleaned_output)
        # Converting string to 2d array
        cleaned_output = ast.literal_eval(cleaned_output)
        
        print(cleaned_output)
        
        if state["candidate_type"] == "person":
            return {**state, "messages": state["messages"] + [AIMessage(str(output))], "person_rubric": {**state["person_rubric"], state["current_category"]: (int(cleaned_output[0][0]), str(cleaned_output[0][1]))}}
        elif state["candidate_type"] == "company":
            return {**state, "messages": state["messages"] + [AIMessage(str(output))], "company_rubric": {**state["company_rubric"], state["current_category"]: (int(cleaned_output[0][0]), str(cleaned_output[0][1]))}}
    else:
        return {**state, "messages": state["messages"] + [AIMessage(str(output))]}


# ==============================================
# Conditional Function Section
# ==============================================

def candidate_processor_conditional(state: State):
    output = state["messages"][-1].content
    if (output == "query_keyword_agent"):
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


def reflection_agent_conditional(state: State):
    
    output = ast.literal_eval(preprocess_json(state["messages"][-1].content))
    decision = output["next_step"]
    if decision == "complete":
        return "category_divider"
    elif decision == "research_issue":
        return "query_vector_db"
    elif decision == "logic_flow_issue":
        return "score_ranking_agent"
    else:
        raise Exception()
    



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
workflow.add_node("add_score_database", add_score_database)
workflow.add_node("rubric_reasoning_agent", rubric_reasoning_agent)
workflow.add_node("generate_queries_agent", generate_queries_agent)
workflow.add_node("query_vector_db", query_vector_db)
workflow.add_node("score_ranking_agent", score_ranking_agent)
workflow.add_node("reflection_agent", reflection_agent)


# Defining the architecture 
workflow.add_edge(START, "init_state")
workflow.add_edge("init_state", "candidate_processor")
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

workflow.add_conditional_edges(
    "reflection_agent",
    reflection_agent_conditional,
    {"category_divider": "category_divider", "query_vector_db": "query_vector_db", "score_ranking_agent": "score_ranking_agent"}
)

workflow.add_edge("query_keyword_agent", "candidate_processor")
workflow.add_edge("rubric_reasoning_agent", "generate_queries_agent")
workflow.add_edge("generate_queries_agent", "query_vector_db")
workflow.add_edge("query_vector_db", "score_ranking_agent")
workflow.add_edge("score_ranking_agent", "reflection_agent")

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