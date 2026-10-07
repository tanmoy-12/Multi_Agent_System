from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

class DependencyDecision(BaseModel):
    relationship: Literal["A_DEPENDS_ON_B", "B_DEPENDS_ON_A", "INDEPENDENT"]
    confidence: float
    reason: str
    required_output: Optional[str] = None

class DependencyEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    from_task: str = Field(alias="from", serialization_alias="from")
    to_task: str = Field(alias="to", serialization_alias="to")
    reason: str
    confidence: float
    score: float = 0.0

class DependencyScore(BaseModel):
    semantic_similarity: float = 0.0
    input_output_match: float = 0.0
    llm_confidence: float = 0.0
    total_score: float = 0.0