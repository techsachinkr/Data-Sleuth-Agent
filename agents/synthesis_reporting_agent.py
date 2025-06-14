import os, sys
sys.path.append(os.getcwd())
from agents.base_agent import BaseAgent
from models.schemas import InvestigationState, IntelligenceReport, Evidence
from typing import List, Dict, Any
import json
import re
from datetime import datetime

class SynthesisReportingAgent(BaseAgent):
    """Agent responsible for synthesizing intelligence and generating comprehensive reports"""
    
    def __init__(self, llm_provider):
        system_prompt = """
        You are an expert intelligence analyst specializing in synthesis and reporting.
        Your role is to:
        1. Aggregate collected intelligence into coherent narratives
        2. Generate structured intelligence reports with confidence scores
        3. Handle large context windows (up to 4M tokens of collected data)
        4. Identify patterns and connections across all collected evidence
        5. Provide actionable intelligence assessments
        
        Your reports should be:
        - Comprehensive yet concise
        - Well-structured with clear sections
        - Include confidence assessments for all claims
        - Highlight key findings and recommendations
        - Identify remaining intelligence gaps
        - Provide strategic recommendations for further investigation
        
        Think like a senior intelligence analyst preparing a briefing for decision-makers.
        """
        super().__init__("Synthesis & Reporting Agent", llm_provider, system_prompt)
    
    async def process(self, state: InvestigationState) -> InvestigationState:
        """Process the investigation state - this is a required abstract method from BaseAgent"""
        # For the synthesis agent, processing means preparing for report generation
        # We don't modify the state here, just ensure it's ready for synthesis
        self.logger.info(f"Synthesis agent processing state for session {state.session_id}")
        
        # Add a processing message to indicate synthesis readiness
        message = self.create_agent_message(
            f"Investigation data processed and ready for synthesis. {len(state.evidence_pool)} evidence items and {len(state.target_entities)} entities analyzed.",
            message_type="synthesis_ready",
            metadata={
                "evidence_count": len(state.evidence_pool),
                "entities_count": len(state.target_entities),
                "conversation_turns": len([msg for msg in state.conversation_history if msg.agent_name == "User"])
            }
        )
        state.conversation_history.append(message)
        
        return state
    
    async def generate_report(self, state: InvestigationState) -> IntelligenceReport:
        """Generate a comprehensive intelligence report"""
        self.logger.info(f"Generating intelligence report for session {state.session_id}")
        
        # Build comprehensive context from all collected data
        context = await self._build_comprehensive_context(state)
        
        report_prompt = f"""
        Generate a comprehensive intelligence report based on all collected data:
        
        INVESTIGATION CONTEXT:
        {context}
        
        Generate a structured report in JSON format:
        {{
            "executive_summary": "High-level summary of key findings and conclusions",
            "key_findings": [
                {{
                    "finding": "Key finding description",
                    "confidence_score": 0.0-1.0,
                    "supporting_evidence": ["evidence1", "evidence2"],
                    "significance": "high|medium|low"
                }}
            ],
            "entity_profiles": [
                {{
                    "entity_name": "Name",
                    "entity_type": "person|organization|location",
                    "profile_summary": "Comprehensive profile based on collected intelligence",
                    "key_attributes": {{"attribute": "value"}},
                    "relationships": ["relationship1", "relationship2"],
                    "confidence_score": 0.0-1.0
                }}
            ],
            "intelligence_assessment": {{
                "overall_confidence": 0.0-1.0,
                "information_quality": "excellent|good|fair|poor",
                "coverage_completeness": 0.0-1.0,
                "reliability_assessment": "high|medium|low"
            }},
            "patterns_and_connections": [
                {{
                    "pattern": "Description of identified pattern",
                    "entities_involved": ["entity1", "entity2"],
                    "significance": "high|medium|low",
                    "confidence": 0.0-1.0
                }}
            ],
            "remaining_gaps": [
                {{
                    "gap_description": "What information is still missing",
                    "priority": "high|medium|low",
                    "recommended_approach": "How to fill this gap"
                }}
            ],
            "strategic_recommendations": [
                {{
                    "recommendation": "Actionable recommendation",
                    "rationale": "Why this recommendation is important",
                    "priority": "high|medium|low",
                    "timeline": "immediate|short-term|long-term"
                }}
            ],
            "appendices": {{
                "evidence_summary": "Summary of all evidence collected",
                "methodology_notes": "Notes on investigation methodology",
                "limitations": "Known limitations of the investigation"
            }}
        }}
        """
        
        try:
            response = await self.generate_response(report_prompt)
            report_data = await self._parse_report_data(response)
            
            # Create structured intelligence report
            report = IntelligenceReport(
                session_id=state.session_id,
                executive_summary=report_data.get("executive_summary", "No summary available"),
                key_findings=report_data.get("key_findings", []),
                confidence_score=report_data.get("intelligence_assessment", {}).get("overall_confidence", state.confidence_score),
                evidence_count=len(state.evidence_pool),
                generated_at=datetime.now(),
                metadata={
                    "entity_profiles": report_data.get("entity_profiles", []),
                    "patterns_and_connections": report_data.get("patterns_and_connections", []),
                    "remaining_gaps": report_data.get("remaining_gaps", []),
                    "strategic_recommendations": report_data.get("strategic_recommendations", []),
                    "intelligence_assessment": report_data.get("intelligence_assessment", {}),
                    "appendices": report_data.get("appendices", {})
                }
            )
            
            # Add report generation message to conversation
            message = self.create_agent_message(
                f"Intelligence report generated with {len(report.key_findings)} key findings and confidence score of {report.confidence_score:.2f}",
                message_type="report",
                metadata={
                    "findings_count": len(report.key_findings),
                    "confidence_score": report.confidence_score,
                    "evidence_analyzed": len(state.evidence_pool)
                }
            )
            state.conversation_history.append(message)
            
            self.logger.info(f"Report generated successfully with {len(report.key_findings)} findings")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            # Return fallback report
            return await self._generate_fallback_report(state)
    
    async def _build_comprehensive_context(self, state: InvestigationState) -> str:
        """Build comprehensive context from all investigation data"""
        context_sections = []
        
        # Original query and objectives
        context_sections.append(f"ORIGINAL QUERY: {state.query}")
        
        # Target entities
        if state.target_entities:
            entities_info = []
            for entity in state.target_entities:
                entity_info = f"{entity.name} ({entity.entity_type.value})"
                if hasattr(entity, 'priority'):
                    entity_info += f" [Priority: {entity.priority}]"
                entities_info.append(entity_info)
            context_sections.append(f"TARGET ENTITIES: {', '.join(entities_info)}")
        
        # Investigation focus areas
        if hasattr(state, 'investigation_focus') and state.investigation_focus:
            context_sections.append(f"INVESTIGATION FOCUS: {', '.join(state.investigation_focus)}")
        
        # Evidence pool analysis
        if state.evidence_pool:
            evidence_summary = self._summarize_evidence_pool(state.evidence_pool)
            context_sections.append(f"EVIDENCE COLLECTED ({len(state.evidence_pool)} items):\n{evidence_summary}")
        
        # Conversation history insights
        if state.conversation_history:
            conversation_summary = self._summarize_conversation_history(state.conversation_history)
            context_sections.append(f"INVESTIGATION PROCESS:\n{conversation_summary}")
        
        # Information gaps
        if state.information_gaps:
            context_sections.append(f"IDENTIFIED GAPS: {', '.join(state.information_gaps[-10:])}")  # Last 10 gaps
        
        # Current questions and focus
        if state.current_questions:
            context_sections.append(f"RECENT QUESTIONS: {'; '.join(state.current_questions)}")
        
        return "\n\n".join(context_sections)
    
    def _summarize_evidence_pool(self, evidence_pool: List[Evidence]) -> str:
        """Summarize the evidence pool for context"""
        if not evidence_pool:
            return "No evidence collected"
        
        # Group evidence by type
        evidence_by_type = {}
        for evidence in evidence_pool:
            evidence_type = evidence.evidence_type.value
            if evidence_type not in evidence_by_type:
                evidence_by_type[evidence_type] = []
            evidence_by_type[evidence_type].append(evidence)
        
        summary_parts = []
        for evidence_type, items in evidence_by_type.items():
            avg_confidence = sum(item.confidence_score for item in items) / len(items)
            summary_parts.append(f"- {evidence_type.title()}: {len(items)} items (avg confidence: {avg_confidence:.2f})")
            
            # Include top evidence items
            top_items = sorted(items, key=lambda x: x.confidence_score, reverse=True)[:3]
            for item in top_items:
                content_preview = item.content[:100] + "..." if len(item.content) > 100 else item.content
                summary_parts.append(f"  • {content_preview} (confidence: {item.confidence_score:.2f})")
        
        return "\n".join(summary_parts)
    
    def _summarize_conversation_history(self, conversation_history) -> str:
        """Summarize the conversation history for context"""
        if not conversation_history:
            return "No conversation history"
        
        # Group messages by agent
        agent_messages = {}
        for message in conversation_history:
            agent_name = message.agent_name
            if agent_name not in agent_messages:
                agent_messages[agent_name] = []
            agent_messages[agent_name].append(message)
        
        summary_parts = []
        for agent_name, messages in agent_messages.items():
            if agent_name == "User":
                summary_parts.append(f"- User provided {len(messages)} responses")
            else:
                summary_parts.append(f"- {agent_name}: {len(messages)} interactions")
                # Include recent significant messages
                recent_messages = messages[-2:]  # Last 2 messages
                for msg in recent_messages:
                    if hasattr(msg, 'metadata') and msg.metadata:
                        summary_parts.append(f"  • {msg.message[:80]}...")
        
        return "\n".join(summary_parts)
    
    async def _parse_report_data(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from report generation"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing report data: {e}")
        
        # Return default structure
        return {
            "executive_summary": "Report generation encountered parsing issues. Raw analysis available in appendices.",
            "key_findings": [],
            "intelligence_assessment": {"overall_confidence": 0.5, "information_quality": "fair"},
            "appendices": {"raw_response": response[:1000]}
        }
    
    async def _generate_fallback_report(self, state: InvestigationState) -> IntelligenceReport:
        """Generate a basic fallback report when main generation fails"""
        self.logger.warning("Generating fallback intelligence report")
        
        # Basic summary based on available data
        summary_parts = []
        summary_parts.append(f"Investigation conducted for query: {state.query}")
        summary_parts.append(f"Collected {len(state.evidence_pool)} pieces of evidence")
        summary_parts.append(f"Analyzed {len(state.target_entities)} target entities")
        
        basic_findings = []
        if state.evidence_pool:
            # Create basic findings from evidence
            high_confidence_evidence = [e for e in state.evidence_pool if e.confidence_score > 0.7]
            for evidence in high_confidence_evidence[:5]:  # Top 5 high-confidence items
                basic_findings.append({
                    "finding": evidence.content[:100] + "..." if len(evidence.content) > 100 else evidence.content,
                    "confidence_score": evidence.confidence_score,
                    "supporting_evidence": [evidence.source],
                    "significance": "medium"
                })
        
        return IntelligenceReport(
            session_id=state.session_id,
            executive_summary=". ".join(summary_parts),
            key_findings=basic_findings,
            confidence_score=state.confidence_score,
            evidence_count=len(state.evidence_pool),
            generated_at=datetime.now(),
            metadata={
                "generation_method": "fallback",
                "limitations": "Report generated using fallback method due to processing issues"
            }
        ) 