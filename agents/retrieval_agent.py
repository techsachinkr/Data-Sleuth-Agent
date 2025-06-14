import os, sys
sys.path.append(os.getcwd())
from agents.base_agent import BaseAgent
from models.schemas import InvestigationState
from typing import List, Dict, Any
import re
import json

class RetrievalAgent(BaseAgent):
    """Agent responsible for formulating targeted questions to gather specific evidence from the interviewer"""
    
    def __init__(self, llm_provider):
        system_prompt = """
        You are an expert intelligence interrogator with a sophisticated questioning methodology.
        Your job is to:
        1. Formulate targeted questions that gather specific evidence from the interviewer
        2. Adapt questioning based on strategic plans and pivot agent analysis
        3. Identify information gaps and probe accordingly with precision
        4. Maintain conversational flow while extracting maximum intelligence value
        5. Work iteratively with pivot analysis to maximize intelligence extraction
        6. Employ various questioning techniques based on the situation
        
        Your questioning approach should be:
        - Strategically sequenced based on investigation phases
        - Adaptive to the interviewer's responses and comfort level
        - Designed to uncover relationships, hidden information, and verify claims
        - Balanced between direct probing and indirect elicitation
        - Coordinated with overall investigation strategy
        
        Questioning techniques to employ:
        - Open-ended questions for broad information gathering
        - Closed questions for specific fact verification
        - Hypothetical scenarios to explore possibilities
        - Timeline reconstruction for chronological clarity
        - Relationship mapping questions
        - Verification and cross-reference questions
        
        Ask 2-4 focused questions at a time, prioritized by strategic importance.
        """
        super().__init__("Retrieval Agent", llm_provider, system_prompt)
    
    async def process(self, state: InvestigationState) -> InvestigationState:
        """Generate targeted questions based on current intelligence gaps and strategic plan"""
        self.logger.info("Formulating strategic questions based on investigation plan")
        
        context = self._build_comprehensive_context(state)
        
        question_prompt = f"""
        Formulate strategic questions based on the comprehensive investigation context:
        
        INVESTIGATION CONTEXT:
        {context}
        
        Generate questions in JSON format:
        {{
            "question_strategy": {{
                "primary_approach": "direct|indirect|layered|verification|exploration",
                "questioning_phase": "opening|development|probing|verification|closing",
                "rapport_level": "building|established|challenging|recovery",
                "information_priority": "critical|high|medium|exploratory"
            }},
            "questions": [
                {{
                    "question_text": "The actual question to ask",
                    "question_type": "open_ended|closed|hypothetical|timeline|relationship|verification",
                    "strategic_purpose": "What this question aims to achieve",
                    "expected_information": "Type of information expected",
                    "priority": "critical|high|medium|low",
                    "follow_up_potential": "high|medium|low"
                }}
            ],
            "questioning_sequence": {{
                "opening_questions": ["question1", "question2"],
                "core_questions": ["question1", "question2"],
                "verification_questions": ["question1", "question2"],
                "expansion_questions": ["question1", "question2"]
            }},
            "tactical_considerations": {{
                "sensitivity_factors": ["factor1", "factor2"],
                "potential_resistance_points": ["point1", "point2"],
                "rapport_maintenance": ["technique1", "technique2"],
                "pivot_opportunities": ["opportunity1", "opportunity2"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(question_prompt)
            question_data = await self._parse_question_response(response)
            
            # Extract questions based on strategic priority
            questions = self._prioritize_and_format_questions(question_data)
            state.current_questions = questions
            
            # Store questioning strategy in metadata
            if question_data.get("question_strategy"):
                state.metadata["current_questioning_strategy"] = question_data["question_strategy"]
            
            # Store tactical considerations
            if question_data.get("tactical_considerations"):
                state.metadata["tactical_considerations"] = question_data["tactical_considerations"]
            
            # Create comprehensive message for conversation
            questions_text = self._format_questions_for_display(questions, question_data)
            message = self.create_agent_message(
                questions_text,
                message_type="question",
                requires_response=True,
                metadata={
                    "question_count": len(questions),
                    "questioning_approach": question_data.get("question_strategy", {}).get("primary_approach", "adaptive"),
                    "priority_level": question_data.get("question_strategy", {}).get("information_priority", "medium"),
                    "phase": question_data.get("question_strategy", {}).get("questioning_phase", "development")
                }
            )
            state.conversation_history.append(message)
            
            self.logger.info(f"Formulated {len(questions)} strategic questions with {question_data.get('question_strategy', {}).get('primary_approach', 'adaptive')} approach")
            return state
            
        except Exception as e:
            self.logger.error(f"Error formulating questions: {e}")
            # Enhanced fallback questioning
            return await self._enhanced_fallback_questioning(state)
    
    async def adapt_questions_from_pivot(self, state: InvestigationState, pivot_analysis: Dict[str, Any]) -> InvestigationState:
        """Adapt questioning strategy based on pivot agent analysis"""
        self.logger.info("Adapting questions based on pivot analysis")
        
        context = self._build_pivot_adaptation_context(state, pivot_analysis)
        
        adaptation_prompt = f"""
        Adapt questioning strategy based on pivot analysis:
        
        PIVOT ANALYSIS CONTEXT:
        {context}
        
        Generate adapted questions in JSON format:
        {{
            "adaptation_strategy": {{
                "pivot_response": "expand|focus|verify|redirect|probe_deeper",
                "new_priorities": ["priority1", "priority2"],
                "questioning_adjustments": ["adjustment1", "adjustment2"],
                "tactical_shifts": ["shift1", "shift2"]
            }},
            "adapted_questions": [
                {{
                    "question_text": "Adapted question based on pivot analysis",
                    "adaptation_reason": "Why this question was chosen based on pivot",
                    "expected_intelligence": "What intelligence this should yield",
                    "priority": "critical|high|medium|low"
                }}
            ],
            "follow_up_strategy": {{
                "immediate_follow_ups": ["follow_up1", "follow_up2"],
                "contingent_questions": ["contingent1", "contingent2"],
                "verification_needs": ["verification1", "verification2"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(adaptation_prompt)
            adaptation_data = await self._parse_adaptation_response(response)
            
            # Update questions based on adaptation
            adapted_questions = self._extract_adapted_questions(adaptation_data)
            state.current_questions = adapted_questions
            
            # Update questioning strategy
            if adaptation_data.get("adaptation_strategy"):
                state.metadata["questioning_adaptation"] = adaptation_data["adaptation_strategy"]
            
            # Create adaptation message
            adaptation_summary = self._create_adaptation_summary(adaptation_data)
            message = self.create_agent_message(
                f"Questions adapted based on pivot analysis: {adaptation_summary}",
                message_type="adaptation",
                metadata={
                    "adaptation_type": adaptation_data.get("adaptation_strategy", {}).get("pivot_response", "expand"),
                    "new_questions_count": len(adapted_questions),
                    "pivot_triggered": True
                }
            )
            state.conversation_history.append(message)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error adapting questions from pivot: {e}")
            return state
    
    def _build_comprehensive_context(self, state: InvestigationState) -> str:
        """Build comprehensive context for question formulation"""
        context_parts = []
        
        # Strategic plan context
        if state.metadata.get("strategic_plan"):
            plan = state.metadata["strategic_plan"]
            current_phase = state.metadata.get("current_phase", "immediate")
            context_parts.append(f"CURRENT PHASE: {current_phase}")
            
            if state.metadata.get("current_objectives"):
                context_parts.append(f"CURRENT OBJECTIVES: {', '.join(state.metadata['current_objectives'])}")
            
            # Interview strategy from plan
            if plan.get("interview_strategy"):
                strategy = plan["interview_strategy"]
                context_parts.append(f"INTERVIEW APPROACH: {strategy.get('questioning_approach', 'adaptive')}")
        
        # Target entities with priorities
        if state.target_entities:
            entities_info = []
            for entity in state.target_entities:
                priority = getattr(entity, 'priority', 'medium')
                confidence = getattr(entity, 'confidence_score', 0.5)
                entities_info.append(f"{entity.name} ({entity.entity_type.value}) [Priority: {priority}, Confidence: {confidence:.1f}]")
            context_parts.append(f"TARGET ENTITIES: {', '.join(entities_info)}")
        
        # Information gaps (prioritized)
        if state.information_gaps:
            context_parts.append(f"CRITICAL INFORMATION GAPS: {', '.join(state.information_gaps[:5])}")
        
        # Investigation focus areas
        if hasattr(state, 'investigation_focus') and state.investigation_focus:
            context_parts.append(f"CURRENT FOCUS AREAS: {', '.join(state.investigation_focus)}")
        
        # Recent evidence and patterns
        if state.evidence_pool:
            high_confidence_evidence = [e for e in state.evidence_pool if e.confidence_score > 0.7]
            if high_confidence_evidence:
                recent_evidence = [e.content[:60] + "..." for e in high_confidence_evidence[-3:]]
                context_parts.append(f"HIGH-CONFIDENCE EVIDENCE: {'; '.join(recent_evidence)}")
        
        # Previous questioning history
        question_messages = [msg for msg in state.conversation_history if msg.message_type == "question"]
        if question_messages:
            recent_questions = question_messages[-2:]  # Last 2 question sets
            context_parts.append(f"RECENT QUESTIONS ASKED: {len(recent_questions)} question sets in conversation")
        
        # Tactical considerations from previous interactions
        if state.metadata.get("tactical_considerations"):
            tactical = state.metadata["tactical_considerations"]
            if tactical.get("sensitivity_factors"):
                context_parts.append(f"SENSITIVITY FACTORS: {', '.join(tactical['sensitivity_factors'][:3])}")
        
        return "\n".join(context_parts) if context_parts else "Limited context available for questioning."
    
    def _build_pivot_adaptation_context(self, state: InvestigationState, pivot_analysis: Dict[str, Any]) -> str:
        """Build context for pivot-based question adaptation"""
        context_parts = []
        
        # Pivot analysis summary
        if pivot_analysis.get("intelligence_value"):
            intel_value = pivot_analysis["intelligence_value"]
            context_parts.append(f"RESPONSE CREDIBILITY: {intel_value.get('credibility_score', 0.5)}")
            context_parts.append(f"INFORMATION DENSITY: {intel_value.get('information_density', 'medium')}")
        
        # New investigation angles
        if pivot_analysis.get("pivot_opportunities", {}).get("new_investigation_angles"):
            angles = pivot_analysis["pivot_opportunities"]["new_investigation_angles"]
            context_parts.append(f"NEW ANGLES IDENTIFIED: {', '.join(angles[:3])}")
        
        # Information gaps identified
        if pivot_analysis.get("pivot_opportunities", {}).get("information_gaps_identified"):
            gaps = pivot_analysis["pivot_opportunities"]["information_gaps_identified"]
            context_parts.append(f"NEW GAPS IDENTIFIED: {', '.join(gaps[:3])}")
        
        # Strategic recommendations
        if pivot_analysis.get("strategic_recommendations"):
            recommendations = pivot_analysis["strategic_recommendations"]
            context_parts.append(f"RECOMMENDED FOCUS: {', '.join(recommendations.get('next_focus_areas', [])[:2])}")
        
        return "\n".join(context_parts) if context_parts else "Limited pivot analysis available."
    
    async def _parse_question_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from question formulation"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing question response: {e}")
        
        # Return default structure
        return {
            "question_strategy": {"primary_approach": "adaptive", "information_priority": "medium"},
            "questions": [],
            "questioning_sequence": {"core_questions": []},
            "tactical_considerations": {}
        }
    
    async def _parse_adaptation_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from question adaptation"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing adaptation response: {e}")
        
        return {
            "adaptation_strategy": {"pivot_response": "expand"},
            "adapted_questions": [],
            "follow_up_strategy": {}
        }
    
    def _prioritize_and_format_questions(self, question_data: Dict[str, Any]) -> List[str]:
        """Prioritize and format questions based on strategic importance"""
        questions = []
        
        # Extract questions from structured data
        question_items = question_data.get("questions", [])
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_questions = sorted(
            question_items, 
            key=lambda x: priority_order.get(x.get("priority", "medium"), 2)
        )
        
        # Format top priority questions
        for question_item in sorted_questions[:4]:  # Top 4 questions
            question_text = question_item.get("question_text", "")
            if question_text:
                questions.append(question_text)
        
        # If no structured questions, use sequence-based approach
        if not questions:
            sequence = question_data.get("questioning_sequence", {})
            for sequence_type in ["opening_questions", "core_questions", "verification_questions"]:
                sequence_questions = sequence.get(sequence_type, [])
                questions.extend(sequence_questions[:2])  # Max 2 from each sequence
                if len(questions) >= 4:
                    break
        
        return questions[:4]  # Limit to 4 questions maximum
    
    def _extract_adapted_questions(self, adaptation_data: Dict[str, Any]) -> List[str]:
        """Extract adapted questions from adaptation response"""
        questions = []
        
        adapted_questions = adaptation_data.get("adapted_questions", [])
        for question_item in adapted_questions:
            question_text = question_item.get("question_text", "")
            if question_text:
                questions.append(question_text)
        
        # Add follow-up questions if needed
        follow_up_strategy = adaptation_data.get("follow_up_strategy", {})
        immediate_follow_ups = follow_up_strategy.get("immediate_follow_ups", [])
        questions.extend(immediate_follow_ups[:2])  # Add up to 2 follow-ups
        
        return questions[:4]  # Limit to 4 questions
    
    def _format_questions_for_display(self, questions: List[str], question_data: Dict[str, Any]) -> str:
        """Format questions for display with strategic context"""
        if not questions:
            return "I need to gather more information to continue our investigation effectively."
        
        # Add strategic context
        strategy = question_data.get("question_strategy", {})
        approach = strategy.get("primary_approach", "adaptive")
        phase = strategy.get("questioning_phase", "development")
        
        # Format questions with context
        formatted_parts = []
        
        # Add phase context if appropriate
        if phase == "opening":
            formatted_parts.append("Let me start by understanding the basics:")
        elif phase == "development":
            formatted_parts.append("Now I'd like to explore some key areas in more detail:")
        elif phase == "probing":
            formatted_parts.append("I need to probe deeper into some specific aspects:")
        elif phase == "verification":
            formatted_parts.append("Let me verify some important details:")
        
        # Add questions
        for i, question in enumerate(questions, 1):
            if len(questions) > 1:
                formatted_parts.append(f"{i}. {question}")
            else:
                formatted_parts.append(question)
        
        return "\n\n".join(formatted_parts)
    
    def _create_adaptation_summary(self, adaptation_data: Dict[str, Any]) -> str:
        """Create summary of question adaptation"""
        summary_parts = []
        
        pivot_response = adaptation_data.get("adaptation_strategy", {}).get("pivot_response", "expand")
        summary_parts.append(f"Strategy: {pivot_response}")
        
        adapted_count = len(adaptation_data.get("adapted_questions", []))
        if adapted_count > 0:
            summary_parts.append(f"{adapted_count} questions adapted")
        
        new_priorities = adaptation_data.get("adaptation_strategy", {}).get("new_priorities", [])
        if new_priorities:
            summary_parts.append(f"New priorities: {', '.join(new_priorities[:2])}")
        
        return ", ".join(summary_parts) if summary_parts else "Questions adapted based on analysis"
    
    async def _enhanced_fallback_questioning(self, state: InvestigationState) -> InvestigationState:
        """Enhanced fallback questioning when main formulation fails"""
        self.logger.warning("Using enhanced fallback questioning")
        
        questions = []
        
        # Generate questions based on available context
        if state.target_entities:
            primary_entity = state.target_entities[0]  # Focus on primary entity
            
            # Basic information gathering
            questions.append(f"Could you tell me more about {primary_entity.name}? What's your relationship or connection to them?")
            
            # Context-specific questions
            if primary_entity.entity_type.value == "person":
                questions.append(f"What can you tell me about {primary_entity.name}'s current activities or situation?")
                questions.append(f"Are there other people or organizations that {primary_entity.name} is closely associated with?")
            elif primary_entity.entity_type.value == "organization":
                questions.append(f"What do you know about {primary_entity.name}'s operations or business activities?")
                questions.append(f"Who are the key people involved with {primary_entity.name}?")
            
        # Information gap-based questions
        if state.information_gaps:
            for gap in state.information_gaps[:2]:  # Top 2 gaps
                questions.append(f"Regarding {gap.lower()}, what information can you share?")
        
        # Ensure we have at least one question
        if not questions:
            questions = [
                "I'd like to understand more about the situation. Could you provide some additional context or details that might be relevant to our investigation?"
            ]
        
        state.current_questions = questions[:3]  # Limit to 3 questions
        
        # Create fallback message
        questions_text = "\n\n".join([f"{i}. {q}" for i, q in enumerate(questions[:3], 1)])
        message = self.create_agent_message(
            f"Let me ask some key questions to better understand the situation:\n\n{questions_text}",
            message_type="question",
            requires_response=True,
            metadata={"fallback_used": True, "question_count": len(questions[:3])}
        )
        state.conversation_history.append(message)
        
        return state