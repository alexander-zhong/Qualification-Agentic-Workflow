"""Define the state structures for the agent. For now just a custom message state"""


from typing_extensions import TypedDict
from typing import Annotated, Optional, Literal, Tuple
from langgraph.graph import MessagesState # prebuilt msg state when needed
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, field_validator, ValidationError



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


class State(TypedDict):
    messages: list[AnyMessage]
    candidate_type: Optional[Literal["person", "company"]]
    current_candidate: Optional[str]
    company_rubric: CompanyRubric
    person_rubric: PersonRubric
    candidate_list: list[Optional[Tuple[str, str]]]
    main_iteration: int
    current_category: Optional[str]
    current_rubric: Optional[str]
    
    
    

