import os,sys
sys.path.append(os.getcwd())
from agents.base_agent import BaseAgent
from models.schemas import InvestigationState, Entity, EntityType
from typing import List, Dict, Any
import re
import json

class QueryAnalysisAgent(BaseAgent):
    """Agent responsible for parsing and understanding customer requests for intelligence on specific entities"""
    
    def __init__(self, llm_provider):
        system_prompt = """
        You are an expert intelligence analyst specializing in query decomposition and entity recognition.
        Your job is to parse customer requests and identify:
        1. Target entities (persons/organizations/locations) with detailed classification
        2. Information types requested (financial, operational, personal, etc.)
        3. Investigation scope, priority, and complexity assessment
        4. Potential intelligence angles and collection requirements
        5. Risk factors and sensitivity levels
        
        You must be thorough in entity extraction, considering:
        - Primary targets (explicitly mentioned)
        - Secondary targets (implied or related)
        - Geographic locations of interest
        - Organizations and their relationships
        - Time frames and historical context
        
        Return your analysis in structured JSON format with confidence scores.
        Be comprehensive but precise in your analysis.
        """
        super().__init__("Query Analysis Agent", llm_provider, system_prompt)
    
    async def process(self, state: InvestigationState) -> InvestigationState:
        """Analyze the incoming query and extract comprehensive intelligence requirements"""
        self.logger.info(f"Analyzing query: {state.query}...")
        
        analysis_prompt = f"""
        Conduct comprehensive intelligence analysis of this request:
        "{state.query}"
        
        Provide detailed JSON response:
        {{
            "query_classification": {{
                "complexity": "simple|moderate|complex|highly_complex",
                "sensitivity_level": "low|medium|high|critical",
                "investigation_type": "person|organization|location|multi-target|relationship_mapping",
                "estimated_scope": "narrow|broad|comprehensive"
            }},
            "primary_entities": [
                {{
                    "name": "entity_name",
                    "type": "person|organization|location",
                    "priority": "critical|high|medium|low",
                    "confidence": 0.0-1.0,
                    "context_clues": ["clue1", "clue2"],
                    "potential_aliases": ["alias1", "alias2"]
                }}
            ],
            "secondary_entities": [
                {{
                    "name": "related_entity",
                    "type": "person|organization|location",
                    "relationship_to_primary": "description",
                    "priority": "high|medium|low"
                }}
            ],
            "information_requirements": {{
                "primary_objectives": ["objective1", "objective2"],
                "information_categories": ["financial", "operational", "personal", "legal", "relationships"],
                "specific_questions": ["question1", "question2"],
                "time_frame": "current|historical|both",
                "geographic_scope": ["location1", "location2"]
            }},
            "collection_strategy": {{
                "recommended_approaches": ["interview", "document_review", "relationship_mapping"],
                "potential_sources": ["source_type1", "source_type2"],
                "collection_priorities": ["priority1", "priority2"],
                "risk_considerations": ["risk1", "risk2"]
            }},
            "success_criteria": {{
                "minimum_requirements": ["requirement1", "requirement2"],
                "optimal_outcomes": ["outcome1", "outcome2"],
                "quality_indicators": ["indicator1", "indicator2"]
            }}
        }}
        """
        
        try:
            response = await self.generate_response(analysis_prompt)
            analysis_data = await self._parse_analysis_response(response)
            
            # Extract and create entity objects
            entities = await self._create_entity_objects(analysis_data)
            state.target_entities = entities
            
            # Set investigation metadata based on analysis
            if analysis_data.get("query_classification"):
                classification = analysis_data["query_classification"]
                state.metadata.update({
                    "complexity": classification.get("complexity", "moderate"),
                    "sensitivity_level": classification.get("sensitivity_level", "medium"),
                    "investigation_type": classification.get("investigation_type", "multi-target"),
                    "estimated_scope": classification.get("estimated_scope", "broad")
                })
            
            # Set information requirements
            if analysis_data.get("information_requirements"):
                info_req = analysis_data["information_requirements"]
                state.information_gaps = info_req.get("primary_objectives", [])
                state.metadata["information_categories"] = info_req.get("information_categories", [])
                state.metadata["specific_questions"] = info_req.get("specific_questions", [])
            
            # Set collection strategy
            if analysis_data.get("collection_strategy"):
                state.metadata["collection_strategy"] = analysis_data["collection_strategy"]
            
            # Add comprehensive analysis message
            message = self.create_agent_message(
                f"Comprehensive query analysis complete. Identified {len(entities)} entities across {len(set(e.entity_type.value for e in entities))} categories. Investigation classified as {state.metadata.get('complexity', 'moderate')} complexity with {state.metadata.get('sensitivity_level', 'medium')} sensitivity.",
                message_type="analysis",
                metadata={
                    "entities_count": len(entities),
                    "primary_entities": len([e for e in entities if getattr(e, 'priority', 'medium') in ['critical', 'high']]),
                    "complexity": state.metadata.get("complexity", "moderate"),
                    "sensitivity": state.metadata.get("sensitivity_level", "medium")
                }
            )
            state.conversation_history.append(message)
            
            self.logger.info(f"Analysis complete. Found {len(entities)} entities with {state.metadata.get('complexity', 'moderate')} complexity")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in query analysis: {e}")
            # Enhanced fallback analysis
            return await self._enhanced_fallback_analysis(state)
    
    async def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from query analysis"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"Error parsing analysis response: {e}")
        
        # Return default structure
        return {
            "query_classification": {"complexity": "moderate", "sensitivity_level": "medium"},
            "primary_entities": [],
            "information_requirements": {"primary_objectives": [], "information_categories": []},
            "collection_strategy": {"recommended_approaches": ["interview"]}
        }
    
    async def _create_entity_objects(self, analysis_data: Dict[str, Any]) -> List[Entity]:
        """Create Entity objects from analysis data"""
        entities = []
        
        # Process primary entities
        primary_entities = analysis_data.get("primary_entities", [])
        for entity_data in primary_entities:
            try:
                entity = Entity(
                    name=entity_data["name"],
                    entity_type=EntityType(entity_data["type"]),
                    priority=entity_data.get("priority", "medium"),
                    confidence_score=entity_data.get("confidence", 0.8),
                    metadata={
                        "context_clues": entity_data.get("context_clues", []),
                        "potential_aliases": entity_data.get("potential_aliases", []),
                        "entity_category": "primary"
                    }
                )
                entities.append(entity)
            except Exception as e:
                self.logger.warning(f"Error creating primary entity {entity_data.get('name', 'unknown')}: {e}")
        
        # Process secondary entities
        secondary_entities = analysis_data.get("secondary_entities", [])
        for entity_data in secondary_entities:
            try:
                entity = Entity(
                    name=entity_data["name"],
                    entity_type=EntityType(entity_data["type"]),
                    priority=entity_data.get("priority", "low"),
                    confidence_score=0.6,  # Lower confidence for secondary entities
                    metadata={
                        "relationship_to_primary": entity_data.get("relationship_to_primary", "unknown"),
                        "entity_category": "secondary"
                    }
                )
                entities.append(entity)
            except Exception as e:
                self.logger.warning(f"Error creating secondary entity {entity_data.get('name', 'unknown')}: {e}")
        
        return entities
    
    async def _enhanced_fallback_analysis(self, state: InvestigationState) -> InvestigationState:
        """Enhanced fallback analysis with better entity extraction"""
        self.logger.warning("Using enhanced fallback analysis")
        
        entities = []
        
        # Enhanced entity extraction using multiple patterns
        query_text = state.query.lower()
        
        # Pattern 1: Proper nouns (potential names)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', state.query)
        
        # Pattern 2: Organization indicators
        org_patterns = [
            r'\b(\w+(?:\s+\w+)*)\s+(?:company|corp|corporation|inc|llc|ltd|organization|agency|department)\b',
            r'\b(?:company|corp|corporation|inc|llc|ltd|organization|agency|department)\s+(\w+(?:\s+\w+)*)\b'
        ]
        
        # Pattern 3: Location indicators
        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        # Extract organizations
        for pattern in org_patterns:
            matches = re.findall(pattern, state.query, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    name=match.strip(),
                    entity_type=EntityType.ORGANIZATION,
                    priority="medium",
                    confidence_score=0.7,
                    metadata={"extraction_method": "pattern_matching", "pattern_type": "organization"}
                ))
        
        # Extract locations
        for pattern in location_patterns:
            matches = re.findall(pattern, state.query)
            for match in matches:
                entities.append(Entity(
                    name=match.strip(),
                    entity_type=EntityType.LOCATION,
                    priority="medium",
                    confidence_score=0.6,
                    metadata={"extraction_method": "pattern_matching", "pattern_type": "location"}
                ))
        
        # Extract potential person names (remaining proper nouns)
        used_names = {e.name.lower() for e in entities}
        for name in proper_nouns:
            if name.lower() not in used_names and len(name.split()) <= 3:  # Reasonable name length
                entities.append(Entity(
                    name=name,
                    entity_type=EntityType.PERSON,
                    priority="medium",
                    confidence_score=0.5,
                    metadata={"extraction_method": "proper_noun_extraction"}
                ))
        
        # Ensure we have at least one entity
        if not entities:
            entities.append(Entity(
                name="Unknown Target",
                entity_type=EntityType.PERSON,
                priority="medium",
                confidence_score=0.3,
                metadata={"extraction_method": "fallback_default"}
            ))
        
        state.target_entities = entities
        
        # Set basic metadata
        state.metadata.update({
            "complexity": "moderate",
            "sensitivity_level": "medium",
            "investigation_type": "multi-target",
            "extraction_method": "enhanced_fallback"
        })
        
        message = self.create_agent_message(
            f"Enhanced fallback analysis complete. Identified {len(entities)} potential entities using pattern matching and linguistic analysis.",
            message_type="warning",
            metadata={"fallback_used": True, "entities_extracted": len(entities)}
        )
        state.conversation_history.append(message)
        
        return state