"""Define the state structures for the agent. For now just a custom message state"""


from typing_extensions import TypedDict
from typing import Annotated, Optional, Literal, Tuple
from langgraph.graph import MessagesState # prebuilt msg state when needed
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, field_validator, ValidationError
import operator


# Keeps track of the message states - we can add more keys here for rubric data and etc.


class PersonRubric(TypedDict):
    expertise_alignment: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    company_relevance: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    geographic_relevance: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    
class CompanyRubric(TypedDict):
    company_mission_alignment: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    relevant_events: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    sponsorship_history: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]
    geographic_relevance: Optional[Tuple[Literal[1, 2, 3, 4, 5], str]
]



def replaceReducer(val1, val2):
    return val2

def objectMergeReducer(val1, val2):
    return {**val1, **val2}

class State(TypedDict):
    messages: Annotated[list[AnyMessage], replaceReducer]
    candidate_type: Annotated[Optional[Literal["person", "company"]], replaceReducer]
    current_candidate: Annotated[Optional[str], replaceReducer]
    company_rubric: Annotated[CompanyRubric, objectMergeReducer]
    person_rubric: Annotated[PersonRubric, objectMergeReducer]
    candidate_list: Annotated[list[Optional[Tuple[str, str]]], replaceReducer]
    main_iteration: Annotated[int, replaceReducer]
    current_category: Annotated[Optional[str], replaceReducer]
    current_rubric: Annotated[Optional[str], replaceReducer]
    reflection_iteration: Annotated[bool, replaceReducer]
