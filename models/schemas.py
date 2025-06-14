from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    RELATIONSHIP = "relationship"

class EvidenceType(str, Enum):
    TESTIMONY = "testimony"
    DOCUMENT = "document"
    INTELLIGENCE = "intelligence"
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    VERIFICATION = "verification"

class InformationQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"

class InvestigationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"

class IntelligenceQueryRequest(BaseModel):
    query: str = Field(..., description="The intelligence query to investigate")
    priority: Optional[str] = Field("medium", description="Investigation priority level")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class Evidence(BaseModel):
    content: str
    source: str
    evidence_type: EvidenceType
    timestamp: datetime
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    entity_mentions: List[str] = []
    relationships: List[Dict[str, Any]] = []

class Entity(BaseModel):
    name: str
    entity_type: EntityType
    priority: str = "medium"
    description: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AgentMessage(BaseModel):
    agent_name: str
    message: str
    timestamp: datetime
    message_type: str = "info"
    requires_response: bool = False
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class InvestigationState(BaseModel):
    session_id: str
    query: str
    status: InvestigationStatus
    target_entities: List[Entity] = []
    evidence_pool: List[Evidence] = []
    conversation_history: List[AgentMessage] = []
    current_questions: List[str] = []
    information_gaps: List[str] = []
    investigation_focus: List[str] = []  # Current focus areas from pivot analysis
    confidence_score: float = 0.0
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)  # For storing strategic plans, phase info, etc.

class IntelligenceReport(BaseModel):
    session_id: str
    executive_summary: str
    key_findings: List[Dict[str, Any]] = []  # Changed to support structured findings
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_count: int
    generated_at: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)  # For entity profiles, patterns, etc.

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)