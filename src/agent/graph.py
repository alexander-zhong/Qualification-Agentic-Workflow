"""
Structure of the category/grader agent - grading company on the rubric of each category
"""



from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState 
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool




# Tool
@tool
def query(message: str):
    """Querys the vector db. The arguments accepted in message str is ONLY company or search_company
    
    Args:
        message: must be "company" or "search_company" without quotations
    """
    if message == "company":
        return "Microsoft"
    else:
        return "Microsoft is a very AI focused company with lots of policies around AI safety"

llm = ChatOpenAI(model="gpt-4o")
rag_llm = llm.bind_tools([query])

sys_msg = SystemMessage(content="You are a search agent that queries for information and give a score on how much you like the company.")

def rag_llm_node(state: MessagesState):
    return {"messages": [rag_llm.invoke([sys_msg] + state["messages"])]}

# tools that the agent has access to
tools = [query]

# Define the agent workflow graph
workflow = StateGraph(MessagesState)

# Add the node to the graph
workflow.add_node("llm", rag_llm_node)
workflow.add_node("tools", ToolNode(tools))

# Defining the architecture 
workflow.add_edge(START, "llm")
workflow.add_conditional_edges(
    "llm",
    tools_condition,
)
workflow.add_edge("tools", "llm")


# Compile the workflow into an executable graph
graph = workflow.compile()
graph.invoke({"messages": {"role": "user", "content": "Can you look at company for me and then search for company?"}})