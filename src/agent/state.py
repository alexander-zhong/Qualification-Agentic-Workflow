"""Define the state structures for the agent. For now just a custom message state"""


from typing_extensions import TypedDict
from typing import Annotated, Optional, Literal
from langgraph.graph import MessagesState # prebuilt msg state when needed
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, field_validator, ValidationError



# Keeps track of the message states - we can add more keys here for rubric data and etc.


class SpeakerRubric(TypedDict):
    speaker_expertise_alignment: Optional[Literal[1, 2, 3, 4, 5]]
    company_relevance: Optional[Literal[1, 2, 3, 4, 5]]
    geographic_relevance: Optional[Literal[1, 2, 3, 4, 5]]
    
class CompanyRubric(TypedDict):
    company_mission_alignment: Optional[Literal[1, 2, 3, 4, 5]]
    relevant_events: Optional[Literal[1, 2, 3, 4, 5]]
    sponsorship_history: Optional[Literal[1, 2, 3, 4, 5]]
    geographic_relevance: Optional[Literal[1, 2, 3, 4, 5]]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # keeping AI context conversation
    candidate_type: Optional[Literal["speaker", "company"]]
    current_candidate: Optional[str]
    company_rubric: CompanyRubric
    speaker_rubric: SpeakerRubric
    candidate_list: list[Optional[str]]
    main_iteration: int
    current_category: Optional[str]
    current_rubric: Optional[str]
    
    
    

