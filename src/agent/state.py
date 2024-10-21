"""Define the state structures for the agent. For now just a custom message state"""


from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import MessagesState # prebuilt msg state when needed
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


# Keeps track of the message states - we can add more keys here for rubric data and etc.
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] 

