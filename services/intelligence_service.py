from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import logging
import os,sys
sys.path.append(os.getcwd())
from models.schemas import (
    InvestigationState, IntelligenceQueryRequest, InvestigationStatus,
    IntelligenceReport, AgentMessage
)

from services.memory_manager import MemoryManager
from services.llm_providers import get_llm_provider

from agents.query_analysis_agent import QueryAnalysisAgent
from agents.planning_agent import PlanningOrchestrationAgent
from agents.retrieval_agent import RetrievalAgent
from agents.pivot_agent import PivotAgent
from agents.synthesis_reporting_agent import SynthesisReportingAgent
# Import other agents as needed



logger = logging.getLogger(__name__)

class IntelligenceService:
    """Main service orchestrating the comprehensive agent-based intelligence gathering pipeline"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.active_investigations: Dict[str, InvestigationState] = {}
        
        # Initialize all agents with LLM providers
        llm_provider = get_llm_provider("gemini-2.5-pro-preview-06-05")
        
        # Core pipeline agents
        self.query_agent = QueryAnalysisAgent(llm_provider)
        self.planning_agent = PlanningOrchestrationAgent(llm_provider)
        self.retrieval_agent = RetrievalAgent(llm_provider)
        self.pivot_agent = PivotAgent(llm_provider)
        self.synthesis_agent = SynthesisReportingAgent(llm_provider)
        
        logger.info("Intelligence service initialized with complete agent pipeline")
    
    async def start_investigation(self, request: IntelligenceQueryRequest) -> InvestigationState:
        """Start a new intelligence investigation using the complete agent pipeline"""
        session_id = str(uuid.uuid4())
        
        state = InvestigationState(
            session_id=session_id,
            query=request.query,
            status=InvestigationStatus.IN_PROGRESS,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}  # Initialize metadata dictionary
        )
        
        self.active_investigations[session_id] = state
        
        try:
            logger.info(f"Starting comprehensive investigation {session_id}")
            
            # Phase 1: Query Analysis - Parse and understand customer requests
            logger.info(f"Phase 1: Query Analysis for {session_id}")
            state = await self.query_agent.process(state)
            
            # Phase 2: Planning & Orchestration - Decompose queries and plan strategy
            logger.info(f"Phase 2: Strategic Planning for {session_id}")
            state = await self.planning_agent.process(state)
            
            # Phase 3: Initial Retrieval - Formulate targeted questions
            logger.info(f"Phase 3: Initial Question Formulation for {session_id}")
            state = await self.retrieval_agent.process(state)
            
            # Set status to waiting for user input
            state.status = InvestigationStatus.WAITING_FOR_INPUT
            state.updated_at = datetime.now()
            
            # Add pipeline initialization message
            pipeline_message = self._create_pipeline_message(state)
            state.conversation_history.append(pipeline_message)
            
            logger.info(f"Investigation {session_id} pipeline initialized successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error starting investigation {session_id}: {e}")
            state.status = InvestigationStatus.FAILED
            raise
    
    async def process_response(self, session_id: str, response: str) -> InvestigationState:
        """Process user response using the Retrieval & Pivot Agent collaboration"""
        if session_id not in self.active_investigations:
            raise ValueError(f"Investigation {session_id} not found")
        
        state = self.active_investigations[session_id]
        
        try:
            logger.info(f"Processing response for {session_id}")
            
            # Add user response to conversation
            user_message = AgentMessage(
                agent_name="User",
                message=response,
                timestamp=datetime.now(),
                message_type="response"
            )
            state.conversation_history.append(user_message)
            
            # Phase 4: Pivot Analysis - Analyze response and identify new angles
            logger.info(f"Phase 4: Pivot Analysis for {session_id}")
            state = await self.pivot_agent.process(state, response)
            
            # Phase 5: Strategy Update - Update strategy based on pivot analysis
            logger.info(f"Phase 5: Strategy Update for {session_id}")
            if hasattr(self.planning_agent, 'update_strategy'):
                state = await self.planning_agent.update_strategy(state)
            
            # Phase 6: Adaptive Retrieval - Generate new questions based on pivot analysis
            logger.info(f"Phase 6: Adaptive Question Generation for {session_id}")
            
            # Check if we should continue questioning or move to synthesis
            if self._should_continue_questioning(state):
                # Get pivot analysis from the last pivot agent message
                pivot_analysis = self._extract_pivot_analysis_from_state(state)
                
                if pivot_analysis and hasattr(self.retrieval_agent, 'adapt_questions_from_pivot'):
                    # Use pivot-adapted questioning
                    state = await self.retrieval_agent.adapt_questions_from_pivot(state, pivot_analysis)
                else:
                    # Use standard questioning
                    state = await self.retrieval_agent.process(state)
                
                state.status = InvestigationStatus.WAITING_FOR_INPUT
            else:
                # Move to synthesis phase
                logger.info(f"Investigation {session_id} ready for synthesis")
                state.status = InvestigationStatus.COMPLETED
                
                # Add completion message
                completion_message = AgentMessage(
                    agent_name="System",
                    message="Investigation phase complete. Sufficient intelligence gathered for comprehensive analysis.",
                    timestamp=datetime.now(),
                    message_type="system",
                    metadata={"phase": "completion", "evidence_count": len(state.evidence_pool)}
                )
                state.conversation_history.append(completion_message)
            
            state.updated_at = datetime.now()
            
            logger.info(f"Response processed for {session_id}. Status: {state.status}")
            return state
            
        except Exception as e:
            logger.error(f"Error processing response for {session_id}: {e}")
            raise
    
    async def generate_report(self, session_id: str) -> IntelligenceReport:
        """Generate comprehensive intelligence report using Synthesis & Reporting Agent"""
        if session_id not in self.active_investigations:
            raise ValueError(f"Investigation {session_id} not found")
        
        state = self.active_investigations[session_id]
        
        try:
            logger.info(f"Generating comprehensive report for {session_id}")
            
            # Phase 7: Synthesis & Reporting - Aggregate intelligence into coherent narratives
            report = await self.synthesis_agent.generate_report(state)
            
            # Update investigation status
            state.status = InvestigationStatus.COMPLETED
            state.updated_at = datetime.now()
            
            # Add report generation message
            report_message = AgentMessage(
                agent_name="Synthesis & Reporting Agent",
                message=f"Comprehensive intelligence report generated with {len(report.key_findings)} key findings and confidence score of {report.confidence_score:.2f}",
                timestamp=datetime.now(),
                message_type="report",
                metadata={
                    "report_id": f"report_{session_id}",
                    "findings_count": len(report.key_findings),
                    "confidence_score": report.confidence_score
                }
            )
            state.conversation_history.append(report_message)
            
            logger.info(f"Report generated successfully for {session_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report for {session_id}: {e}")
            raise
    
    def get_investigation_state(self, session_id: str) -> Optional[InvestigationState]:
        """Get current investigation state"""
        return self.active_investigations.get(session_id)
    
    def _create_pipeline_message(self, state: InvestigationState) -> AgentMessage:
        """Create a message summarizing the pipeline initialization"""
        entities_count = len(state.target_entities)
        complexity = state.metadata.get("complexity", "moderate")
        current_phase = state.metadata.get("current_phase", "immediate")
        
        message_text = (
            f"Intelligence gathering pipeline initialized. "
            f"Identified {entities_count} target entities with {complexity} complexity. "
            f"Investigation proceeding in {current_phase} phase with strategic questioning approach."
        )
        
        return AgentMessage(
            agent_name="Intelligence Pipeline",
            message=message_text,
            timestamp=datetime.now(),
            message_type="system",
            metadata={
                "pipeline_phase": "initialization",
                "entities_count": entities_count,
                "complexity": complexity,
                "current_phase": current_phase
            }
        )
    
    def _should_continue_questioning(self, state: InvestigationState) -> bool:
        """Determine if investigation should continue with more questions or move to synthesis"""
        
        # Check evidence threshold
        evidence_count = len(state.evidence_pool)
        min_evidence_threshold = 5  # Minimum pieces of evidence
        
        # Check confidence score
        confidence_threshold = 0.7  # Minimum confidence for completion
        
        # Check conversation length (avoid infinite loops)
        max_conversation_length = 20  # Maximum conversation turns
        conversation_length = len([msg for msg in state.conversation_history if msg.agent_name == "User"])
        
        # Check if we have sufficient information
        information_gaps = len(state.information_gaps)
        max_gaps_threshold = 3  # Maximum acceptable information gaps
        
        # Decision logic
        continue_questioning = (
            evidence_count < min_evidence_threshold or
            state.confidence_score < confidence_threshold or
            information_gaps > max_gaps_threshold
        ) and conversation_length < max_conversation_length
        
        # Check phase completion criteria
        current_phase = state.metadata.get("current_phase", "immediate")
        phase_status = state.metadata.get("phase_status", "on_track")
        
        # If current phase is complete and ready for next phase
        if phase_status == "on_track" and current_phase == "exploitation":
            continue_questioning = False
        
        logger.info(
            f"Questioning decision for {state.session_id}: "
            f"Evidence: {evidence_count}/{min_evidence_threshold}, "
            f"Confidence: {state.confidence_score:.2f}/{confidence_threshold}, "
            f"Gaps: {information_gaps}/{max_gaps_threshold}, "
            f"Turns: {conversation_length}/{max_conversation_length}, "
            f"Continue: {continue_questioning}"
        )
        
        return continue_questioning
    
    def _extract_pivot_analysis_from_state(self, state: InvestigationState) -> Optional[Dict[str, Any]]:
        """Extract pivot analysis data from the most recent pivot agent message"""
        
        # Look for the most recent pivot agent message
        pivot_messages = [
            msg for msg in state.conversation_history 
            if msg.agent_name == "Pivot Agent" and msg.message_type == "analysis"
        ]
        
        if not pivot_messages:
            return None
        
        latest_pivot_message = pivot_messages[-1]
        
        # Extract analysis data from metadata if available
        if hasattr(latest_pivot_message, 'metadata') and latest_pivot_message.metadata:
            # Create a simplified pivot analysis structure
            return {
                "intelligence_value": {
                    "credibility_score": latest_pivot_message.metadata.get("credibility_score", 0.5),
                    "information_density": "medium"
                },
                "pivot_opportunities": {
                    "new_investigation_angles": state.investigation_focus if hasattr(state, 'investigation_focus') else [],
                    "information_gaps_identified": state.information_gaps[-3:] if state.information_gaps else []
                },
                "strategic_recommendations": {
                    "next_focus_areas": state.investigation_focus[:2] if hasattr(state, 'investigation_focus') else []
                }
            }
        
        return None
    
    async def get_investigation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the investigation progress"""
        if session_id not in self.active_investigations:
            raise ValueError(f"Investigation {session_id} not found")
        
        state = self.active_investigations[session_id]
        
        return {
            "session_id": session_id,
            "status": state.status.value,
            "entities_identified": len(state.target_entities),
            "evidence_collected": len(state.evidence_pool),
            "confidence_score": state.confidence_score,
            "information_gaps": len(state.information_gaps),
            "conversation_turns": len([msg for msg in state.conversation_history if msg.agent_name == "User"]),
            "current_phase": state.metadata.get("current_phase", "unknown"),
            "complexity": state.metadata.get("complexity", "unknown"),
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat()
        }