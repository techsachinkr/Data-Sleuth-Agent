import os, sys
sys.path.append(os.getcwd())
from agents.base_agent import BaseAgent
from models.schemas import InvestigationState, Evidence, EvidenceType
from typing import List, Dict, Any
import json
import re
from datetime import datetime

class PivotAgent(BaseAgent):
    """Agent responsible for analyzing responses and identifying new investigation angles"""
    
    def __init__(self, llm_provider):
        system_prompt = """
        You are an expert intelligence analyst specializing in pivot analysis and strategic redirection.
        Your role is to:
        1. Analyze user responses for intelligence value and credibility
        2. Identify new investigation angles and connections
        3. Spot information gaps and inconsistencies
        4. Generate follow-up questions that maximize intelligence extraction
        5. Assess the reliability and significance of collected information
        
        Think like a seasoned intelligence officer who can:
        - Read between the lines
        - Identify what's NOT being said
        - Connect disparate pieces of information
        - Pivot investigation focus based on new revelations
        - Assess source credibility and information quality
        
        Always look for opportunities to expand the investigation scope strategically.
        """
        super().__init__("Pivot Agent", llm_provider, system_prompt)
    
    async def process(self, state: InvestigationState, user_response: str) -> InvestigationState:
        """Analyze user response and identify pivot opportunities"""
        self.logger.info("Analyzing response for pivot opportunities")
        
        context = self._build_analysis_context(state, user_response)
        
        pivot_prompt = f"""
        Analyze this intelligence response and identify pivot opportunities:
        
        CONTEXT:
        {context}
        
        USER RESPONSE:
        "{user_response}"
        
        Provide analysis in JSON format:
        {{
            "intelligence_value": {{
                "credibility_score": 0.0-1.0,
                "information_density": "low|medium|high",
                "new_entities_mentioned": ["entity1", "entity2"],
                "key_revelations": ["revelation1", "revelation2"]
            }},
            "pivot_opportunities": {{
                "new_investigation_angles": ["angle1", "angle2"],
                "follow_up_priorities": ["priority1", "priority2"],
                "information_gaps_identified": ["gap1", "gap2"],
                "potential_connections": ["connection1", "connection2"]
            }},
            "strategic_recommendations": {{
                "next_focus_areas": ["area1", "area2"],
                "questioning_strategy": "direct|indirect|probing|verification",
                "investigation_expansion": ["expand_to1", "expand_to2"]
            }},
            "evidence_assessment": {{
                "actionable_intelligence": ["intel1", "intel2"],
                "requires_verification": ["claim1", "claim2"],
                "contradictions_noted": ["contradiction1"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(pivot_prompt)
            analysis = await self._parse_pivot_analysis(response)
            
            # Extract and store evidence from the response
            evidence_items = await self._extract_evidence(user_response, analysis)
            state.evidence_pool.extend(evidence_items)
            
            # Update information gaps based on analysis
            if analysis.get("pivot_opportunities", {}).get("information_gaps_identified"):
                state.information_gaps.extend(
                    analysis["pivot_opportunities"]["information_gaps_identified"]
                )
            
            # Update investigation focus if new angles identified
            new_angles = analysis.get("pivot_opportunities", {}).get("new_investigation_angles", [])
            if new_angles:
                state.investigation_focus = new_angles[:3]  # Top 3 new angles
            
            # Create pivot analysis message
            pivot_summary = self._create_pivot_summary(analysis)
            message = self.create_agent_message(
                f"Pivot analysis complete: {pivot_summary}",
                message_type="analysis",
                metadata={
                    "credibility_score": analysis.get("intelligence_value", {}).get("credibility_score", 0.5),
                    "new_angles_count": len(new_angles),
                    "evidence_extracted": len(evidence_items)
                }
            )
            state.conversation_history.append(message)
            
            # Update confidence score based on analysis
            credibility = analysis.get("intelligence_value", {}).get("credibility_score", 0.5)
            state.confidence_score = min(1.0, state.confidence_score + (credibility * 0.1))
            
            self.logger.info(f"Pivot analysis complete. Found {len(new_angles)} new angles, extracted {len(evidence_items)} evidence items")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in pivot analysis: {e}")
            # Fallback: basic evidence extraction
            return await self._fallback_pivot_analysis(state, user_response)
    
    async def _parse_pivot_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from pivot analysis"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing pivot analysis: {e}")
        
        # Return default structure
        return {
            "intelligence_value": {"credibility_score": 0.5, "information_density": "medium"},
            "pivot_opportunities": {"new_investigation_angles": [], "information_gaps_identified": []},
            "strategic_recommendations": {"next_focus_areas": [], "questioning_strategy": "probing"},
            "evidence_assessment": {"actionable_intelligence": [], "requires_verification": []}
        }
    
    async def _extract_evidence(self, user_response: str, analysis: Dict[str, Any]) -> List[Evidence]:
        """Extract evidence items from user response based on analysis"""
        evidence_items = []
        
        # Extract actionable intelligence as evidence
        actionable_intel = analysis.get("evidence_assessment", {}).get("actionable_intelligence", [])
        for intel in actionable_intel:
            evidence = Evidence(
                content=intel,
                source="user_interview",
                evidence_type=EvidenceType.TESTIMONY,
                confidence_score=analysis.get("intelligence_value", {}).get("credibility_score", 0.5),
                timestamp=datetime.now(),
                metadata={"extracted_from": "pivot_analysis"}
            )
            evidence_items.append(evidence)
        
        # Extract key revelations as evidence
        revelations = analysis.get("intelligence_value", {}).get("key_revelations", [])
        for revelation in revelations:
            evidence = Evidence(
                content=revelation,
                source="user_interview",
                evidence_type=EvidenceType.INTELLIGENCE,
                confidence_score=analysis.get("intelligence_value", {}).get("credibility_score", 0.5),
                timestamp=datetime.now(),
                metadata={"type": "revelation", "extracted_from": "pivot_analysis"}
            )
            evidence_items.append(evidence)
        
        return evidence_items
    
    def _create_pivot_summary(self, analysis: Dict[str, Any]) -> str:
        """Create a summary of the pivot analysis"""
        summary_parts = []
        
        credibility = analysis.get("intelligence_value", {}).get("credibility_score", 0.5)
        summary_parts.append(f"Credibility: {credibility:.1f}")
        
        new_angles = len(analysis.get("pivot_opportunities", {}).get("new_investigation_angles", []))
        if new_angles > 0:
            summary_parts.append(f"{new_angles} new investigation angles identified")
        
        gaps = len(analysis.get("pivot_opportunities", {}).get("information_gaps_identified", []))
        if gaps > 0:
            summary_parts.append(f"{gaps} information gaps identified")
        
        return ", ".join(summary_parts) if summary_parts else "Basic analysis completed"
    
    def _build_analysis_context(self, state: InvestigationState, user_response: str) -> str:
        """Build context for pivot analysis"""
        context_parts = []
        
        # Target entities
        if state.target_entities:
            entities = [f"{e.name} ({e.entity_type.value})" for e in state.target_entities]
            context_parts.append(f"Target Entities: {', '.join(entities)}")
        
        # Recent questions asked
        if state.current_questions:
            context_parts.append(f"Recent Questions: {'; '.join(state.current_questions[-2:])}")
        
        # Existing evidence
        if state.evidence_pool:
            recent_evidence = [e.content for e in state.evidence_pool[-3:]]
            context_parts.append(f"Recent Evidence: {'; '.join(recent_evidence)}")
        
        # Current information gaps
        if state.information_gaps:
            context_parts.append(f"Known Gaps: {'; '.join(state.information_gaps[-3:])}")
        
        return "\n".join(context_parts) if context_parts else "No prior context available."
    
    async def _fallback_pivot_analysis(self, state: InvestigationState, user_response: str) -> InvestigationState:
        """Fallback pivot analysis when main analysis fails"""
        self.logger.warning("Using fallback pivot analysis")
        
        # Basic evidence extraction
        evidence = Evidence(
            content=user_response[:200] + "..." if len(user_response) > 200 else user_response,
            source="user_interview",
            evidence_type=EvidenceType.TESTIMONY,
            confidence_score=0.6,
            timestamp=datetime.now(),
            metadata={"extraction_method": "fallback"}
        )
        state.evidence_pool.append(evidence)
        
        # Add basic analysis message
        message = self.create_agent_message(
            "Basic pivot analysis completed. Response recorded as evidence.",
            message_type="warning",
            metadata={"fallback_used": True}
        )
        state.conversation_history.append(message)
        
        return state 