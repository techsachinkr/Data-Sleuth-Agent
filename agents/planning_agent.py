import os,sys
sys.path.append(os.getcwd())
from agents.base_agent import BaseAgent
from models.schemas import InvestigationState
from typing import Dict, Any, List
import json
import re

class PlanningOrchestrationAgent(BaseAgent):
    """Agent responsible for strategic planning, orchestration, and dynamic interview strategy development"""
    
    def __init__(self, llm_provider):
        system_prompt = """
        You are a master intelligence strategist and orchestration expert. Your role is to:
        1. Decompose queries into strategic information gathering tasks
        2. Dynamically plan interview strategies to extract maximum intelligence
        3. Coordinate between retrieval and pivot agents for optimal information flow
        4. Adapt strategies based on collected intelligence and emerging patterns
        5. Maximize information extraction through strategic questioning sequences
        6. Manage investigation priorities and resource allocation
        
        Think like a seasoned intelligence operations manager who:
        - Plans multi-phase operations with clear objectives
        - Adapts tactics based on real-time intelligence
        - Coordinates multiple collection streams
        - Identifies critical decision points and pivot opportunities
        - Balances depth vs breadth in information gathering
        - Manages operational security and source protection
        
        Your plans should be actionable, adaptive, and strategically sound.
        Focus on maximizing intelligence value while maintaining operational efficiency.
        """
        super().__init__("Planning & Orchestration Agent", llm_provider, system_prompt)
    
    async def process(self, state: InvestigationState) -> InvestigationState:
        """Create a comprehensive strategic plan for intelligence gathering"""
        self.logger.info("Creating comprehensive investigation plan")
        
        context = self._build_planning_context(state)
        
        planning_prompt = f"""
        Develop a comprehensive intelligence gathering strategy:
        
        INVESTIGATION CONTEXT:
        {context}
        
        Create a strategic plan in JSON format:
        {{
            "mission_analysis": {{
                "primary_objectives": ["objective1", "objective2"],
                "success_criteria": ["criteria1", "criteria2"],
                "critical_information_requirements": ["requirement1", "requirement2"],
                "priority_intelligence_targets": ["target1", "target2"]
            }},
            "collection_strategy": {{
                "phase_1_immediate": {{
                    "objectives": ["immediate_objective1", "immediate_objective2"],
                    "collection_methods": ["method1", "method2"],
                    "expected_outcomes": ["outcome1", "outcome2"],
                    "success_indicators": ["indicator1", "indicator2"]
                }},
                "phase_2_development": {{
                    "objectives": ["development_objective1", "development_objective2"],
                    "collection_methods": ["method1", "method2"],
                    "pivot_opportunities": ["pivot1", "pivot2"],
                    "expansion_targets": ["target1", "target2"]
                }},
                "phase_3_exploitation": {{
                    "objectives": ["exploitation_objective1", "exploitation_objective2"],
                    "synthesis_requirements": ["requirement1", "requirement2"],
                    "verification_needs": ["verification1", "verification2"]
                }}
            }},
            "interview_strategy": {{
                "questioning_approach": "direct|indirect|layered|adaptive",
                "rapport_building": ["technique1", "technique2"],
                "information_elicitation": ["technique1", "technique2"],
                "verification_methods": ["method1", "method2"],
                "pivot_triggers": ["trigger1", "trigger2"]
            }},
            "coordination_plan": {{
                "retrieval_agent_tasks": ["task1", "task2"],
                "pivot_agent_triggers": ["trigger1", "trigger2"],
                "synthesis_checkpoints": ["checkpoint1", "checkpoint2"],
                "quality_control_measures": ["measure1", "measure2"]
            }},
            "risk_management": {{
                "operational_risks": ["risk1", "risk2"],
                "information_security": ["measure1", "measure2"],
                "source_protection": ["protection1", "protection2"],
                "contingency_plans": ["plan1", "plan2"]
            }},
            "resource_allocation": {{
                "time_estimates": {{"phase_1": "estimate", "phase_2": "estimate", "phase_3": "estimate"}},
                "priority_distribution": {{"high": 40, "medium": 35, "low": 25}},
                "collection_focus": ["focus_area1", "focus_area2"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(planning_prompt)
            plan_data = await self._parse_planning_response(response)
            
            # Store the strategic plan in state metadata
            state.metadata["strategic_plan"] = plan_data
            
            # Set immediate objectives and priorities
            if plan_data.get("mission_analysis"):
                mission = plan_data["mission_analysis"]
                state.information_gaps = mission.get("critical_information_requirements", state.information_gaps)
                state.metadata["primary_objectives"] = mission.get("primary_objectives", [])
                state.metadata["success_criteria"] = mission.get("success_criteria", [])
            
            # Set current phase and tasks
            if plan_data.get("collection_strategy", {}).get("phase_1_immediate"):
                phase_1 = plan_data["collection_strategy"]["phase_1_immediate"]
                state.metadata["current_phase"] = "immediate"
                state.metadata["current_objectives"] = phase_1.get("objectives", [])
                state.metadata["expected_outcomes"] = phase_1.get("expected_outcomes", [])
            
            # Set interview strategy
            if plan_data.get("interview_strategy"):
                state.metadata["interview_strategy"] = plan_data["interview_strategy"]
            
            # Set coordination parameters
            if plan_data.get("coordination_plan"):
                state.metadata["coordination_plan"] = plan_data["coordination_plan"]
            
            # Create comprehensive planning message
            plan_summary = self._create_plan_summary(plan_data, state)
            message = self.create_agent_message(
                f"Strategic investigation plan developed: {plan_summary}",
                message_type="planning",
                metadata={
                    "plan_complexity": len(plan_data.get("collection_strategy", {})),
                    "phases_planned": len([k for k in plan_data.get("collection_strategy", {}).keys() if k.startswith("phase_")]),
                    "objectives_count": len(state.metadata.get("primary_objectives", [])),
                    "current_phase": state.metadata.get("current_phase", "immediate")
                }
            )
            state.conversation_history.append(message)
            
            self.logger.info(f"Strategic plan created with {len(state.metadata.get('primary_objectives', []))} objectives")
            return state
            
        except Exception as e:
            self.logger.error(f"Error creating investigation plan: {e}")
            # Fallback to basic planning
            return await self._create_fallback_plan(state)
    
    async def update_strategy(self, state: InvestigationState) -> InvestigationState:
        """Update strategy based on collected intelligence and pivot analysis"""
        self.logger.info("Updating investigation strategy based on new intelligence")
        
        context = self._build_strategy_update_context(state)
        
        update_prompt = f"""
        Update the investigation strategy based on new intelligence:
        
        CURRENT SITUATION:
        {context}
        
        Provide strategy updates in JSON format:
        {{
            "strategy_assessment": {{
                "current_phase_status": "on_track|needs_adjustment|pivot_required",
                "objective_completion": {{"completed": [], "in_progress": [], "blocked": []}},
                "new_opportunities": ["opportunity1", "opportunity2"],
                "emerging_priorities": ["priority1", "priority2"]
            }},
            "tactical_adjustments": {{
                "questioning_modifications": ["modification1", "modification2"],
                "focus_shifts": ["shift1", "shift2"],
                "new_collection_targets": ["target1", "target2"],
                "pivot_recommendations": ["recommendation1", "recommendation2"]
            }},
            "next_phase_preparation": {{
                "readiness_assessment": "ready|needs_more_intel|major_gaps",
                "transition_triggers": ["trigger1", "trigger2"],
                "preparation_tasks": ["task1", "task2"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(update_prompt)
            update_data = await self._parse_strategy_update(response)
            
            # Apply strategy updates
            if update_data.get("strategy_assessment"):
                assessment = update_data["strategy_assessment"]
                state.metadata["phase_status"] = assessment.get("current_phase_status", "on_track")
                
                # Update objectives based on completion status
                if assessment.get("objective_completion"):
                    completion = assessment["objective_completion"]
                    state.metadata["completed_objectives"] = completion.get("completed", [])
                    state.metadata["blocked_objectives"] = completion.get("blocked", [])
                
                # Add new opportunities to information gaps
                new_opportunities = assessment.get("new_opportunities", [])
                state.information_gaps.extend(new_opportunities)
            
            # Apply tactical adjustments
            if update_data.get("tactical_adjustments"):
                adjustments = update_data["tactical_adjustments"]
                state.metadata["tactical_adjustments"] = adjustments
                
                # Update focus areas
                focus_shifts = adjustments.get("focus_shifts", [])
                if focus_shifts:
                    state.investigation_focus = focus_shifts[:3]  # Top 3 focus areas
            
            # Prepare for next phase if ready
            if update_data.get("next_phase_preparation"):
                prep = update_data["next_phase_preparation"]
                state.metadata["next_phase_readiness"] = prep.get("readiness_assessment", "needs_more_intel")
                
                if prep.get("readiness_assessment") == "ready":
                    await self._advance_to_next_phase(state)
            
            # Create strategy update message
            update_summary = self._create_update_summary(update_data)
            message = self.create_agent_message(
                f"Strategy updated: {update_summary}",
                message_type="strategy_update",
                metadata={
                    "phase_status": state.metadata.get("phase_status", "on_track"),
                    "new_opportunities": len(update_data.get("strategy_assessment", {}).get("new_opportunities", [])),
                    "tactical_adjustments": len(update_data.get("tactical_adjustments", {}))
                }
            )
            state.conversation_history.append(message)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error updating strategy: {e}")
            return state
    
    def _build_planning_context(self, state: InvestigationState) -> str:
        """Build context for strategic planning"""
        context_parts = []
        
        # Original query and classification
        context_parts.append(f"ORIGINAL QUERY: {state.query}")
        
        if state.metadata.get("complexity"):
            context_parts.append(f"COMPLEXITY: {state.metadata['complexity']}")
            context_parts.append(f"SENSITIVITY: {state.metadata.get('sensitivity_level', 'medium')}")
        
        # Target entities with priorities
        if state.target_entities:
            entities_info = []
            for entity in state.target_entities:
                priority = getattr(entity, 'priority', 'medium')
                entities_info.append(f"{entity.name} ({entity.entity_type.value}) [Priority: {priority}]")
            context_parts.append(f"TARGET ENTITIES: {', '.join(entities_info)}")
        
        # Information requirements
        if state.metadata.get("information_categories"):
            context_parts.append(f"INFORMATION CATEGORIES: {', '.join(state.metadata['information_categories'])}")
        
        # Collection strategy from query analysis
        if state.metadata.get("collection_strategy"):
            strategy = state.metadata["collection_strategy"]
            context_parts.append(f"RECOMMENDED APPROACHES: {', '.join(strategy.get('recommended_approaches', []))}")
        
        # Current information gaps
        if state.information_gaps:
            context_parts.append(f"INFORMATION GAPS: {', '.join(state.information_gaps[:5])}")  # Top 5 gaps
        
        return "\n".join(context_parts)
    
    def _build_strategy_update_context(self, state: InvestigationState) -> str:
        """Build context for strategy updates"""
        context_parts = []
        
        # Current phase and objectives
        current_phase = state.metadata.get("current_phase", "immediate")
        context_parts.append(f"CURRENT PHASE: {current_phase}")
        
        if state.metadata.get("current_objectives"):
            context_parts.append(f"CURRENT OBJECTIVES: {', '.join(state.metadata['current_objectives'])}")
        
        # Evidence collected
        if state.evidence_pool:
            context_parts.append(f"EVIDENCE COLLECTED: {len(state.evidence_pool)} items")
            recent_evidence = [e.content[:50] + "..." for e in state.evidence_pool[-3:]]
            context_parts.append(f"RECENT EVIDENCE: {'; '.join(recent_evidence)}")
        
        # Investigation focus
        if hasattr(state, 'investigation_focus') and state.investigation_focus:
            context_parts.append(f"CURRENT FOCUS: {', '.join(state.investigation_focus)}")
        
        # Phase status
        if state.metadata.get("phase_status"):
            context_parts.append(f"PHASE STATUS: {state.metadata['phase_status']}")
        
        return "\n".join(context_parts)
    
    async def _parse_planning_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from strategic planning"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing planning response: {e}")
        
        # Return default structure
        return {
            "mission_analysis": {"primary_objectives": [], "critical_information_requirements": []},
            "collection_strategy": {"phase_1_immediate": {"objectives": [], "collection_methods": []}},
            "interview_strategy": {"questioning_approach": "adaptive"},
            "coordination_plan": {"retrieval_agent_tasks": [], "pivot_agent_triggers": []}
        }
    
    async def _parse_strategy_update(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from strategy updates"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing strategy update: {e}")
        
        return {
            "strategy_assessment": {"current_phase_status": "on_track"},
            "tactical_adjustments": {},
            "next_phase_preparation": {"readiness_assessment": "needs_more_intel"}
        }
    
    def _create_plan_summary(self, plan_data: Dict[str, Any], state: InvestigationState) -> str:
        """Create a summary of the strategic plan"""
        summary_parts = []
        
        # Objectives count
        objectives = plan_data.get("mission_analysis", {}).get("primary_objectives", [])
        if objectives:
            summary_parts.append(f"{len(objectives)} primary objectives")
        
        # Phases planned
        collection_strategy = plan_data.get("collection_strategy", {})
        phases = [k for k in collection_strategy.keys() if k.startswith("phase_")]
        if phases:
            summary_parts.append(f"{len(phases)} phases planned")
        
        # Interview approach
        interview_approach = plan_data.get("interview_strategy", {}).get("questioning_approach", "adaptive")
        summary_parts.append(f"{interview_approach} questioning approach")
        
        # Current phase
        current_phase = state.metadata.get("current_phase", "immediate")
        summary_parts.append(f"starting with {current_phase} phase")
        
        return ", ".join(summary_parts) if summary_parts else "Basic strategic plan established"
    
    def _create_update_summary(self, update_data: Dict[str, Any]) -> str:
        """Create a summary of strategy updates"""
        summary_parts = []
        
        # Phase status
        phase_status = update_data.get("strategy_assessment", {}).get("current_phase_status", "on_track")
        summary_parts.append(f"Phase status: {phase_status}")
        
        # New opportunities
        new_opportunities = update_data.get("strategy_assessment", {}).get("new_opportunities", [])
        if new_opportunities:
            summary_parts.append(f"{len(new_opportunities)} new opportunities identified")
        
        # Tactical adjustments
        adjustments = update_data.get("tactical_adjustments", {})
        if adjustments:
            summary_parts.append(f"Tactical adjustments applied")
        
        return ", ".join(summary_parts) if summary_parts else "Strategy maintained"
    
    async def _advance_to_next_phase(self, state: InvestigationState) -> None:
        """Advance investigation to the next phase"""
        current_phase = state.metadata.get("current_phase", "immediate")
        
        phase_progression = {
            "immediate": "development",
            "development": "exploitation",
            "exploitation": "synthesis"
        }
        
        next_phase = phase_progression.get(current_phase, "synthesis")
        state.metadata["current_phase"] = next_phase
        
        # Update objectives for new phase
        strategic_plan = state.metadata.get("strategic_plan", {})
        collection_strategy = strategic_plan.get("collection_strategy", {})
        
        phase_key = f"phase_2_{next_phase}" if next_phase == "development" else f"phase_3_{next_phase}"
        if phase_key in collection_strategy:
            phase_data = collection_strategy[phase_key]
            state.metadata["current_objectives"] = phase_data.get("objectives", [])
        
        self.logger.info(f"Advanced investigation to {next_phase} phase")
    
    async def _create_fallback_plan(self, state: InvestigationState) -> InvestigationState:
        """Create a basic fallback plan when main planning fails"""
        self.logger.warning("Creating fallback strategic plan")
        
        # Basic objectives based on entities
        entities_summary = ", ".join([e.name for e in state.target_entities])
        
        # Set basic plan structure
        state.metadata["strategic_plan"] = {
            "mission_analysis": {
                "primary_objectives": [f"Gather intelligence on {entities_summary}"],
                "critical_information_requirements": state.information_gaps or ["Basic entity information"]
            },
            "collection_strategy": {
                "phase_1_immediate": {
                    "objectives": ["Establish baseline information", "Identify key relationships"],
                    "collection_methods": ["interview", "direct_questioning"]
                }
            },
            "interview_strategy": {"questioning_approach": "direct"}
        }
        
        state.metadata["current_phase"] = "immediate"
        state.metadata["primary_objectives"] = [f"Gather intelligence on {entities_summary}"]
        
        message = self.create_agent_message(
            f"Basic strategic plan created focusing on {entities_summary}. Using direct questioning approach.",
            message_type="planning",
            metadata={"fallback_used": True, "plan_focus": entities_summary}
        )
        state.conversation_history.append(message)
        
        return state