from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.schemas import InvestigationState, AgentMessage
from services.llm_providers import LLMProvider
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all intelligence agents"""
    
    def __init__(self, name: str, llm_provider: LLMProvider, system_prompt: str):
        self.name = name
        self.llm = llm_provider
        self.system_prompt = system_prompt
        self.logger = logging.getLogger(f"agents.{name.lower().replace(' ', '_')}")
    
    @abstractmethod
    async def process(self, state: InvestigationState) -> InvestigationState:
        """Process the current investigation state"""
        pass
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate LLM response with error handling"""
        try:
            response = await self.llm.generate(prompt, self.system_prompt, **kwargs)
            self.logger.info(f"Generated response of length {len(response)}")
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def create_agent_message(
        self, 
        message: str, 
        message_type: str = "info", 
        requires_response: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """Create a standardized agent message"""
        return AgentMessage(
            agent_name=self.name,
            message=message,
            timestamp=datetime.now(),
            message_type=message_type,
            requires_response=requires_response,
            metadata=metadata or {})