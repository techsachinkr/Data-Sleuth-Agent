# Data Sleuth Agent System - Agent-Based Pipeline Overview

## System Architecture

The Data Sleuth Agent System has been updated to implement a comprehensive agent-based pipeline that follows the specified constraints for strategic intelligence gathering and analysis.

## Agent-Based Pipeline Components

### 1. Query Analysis Agent (`agents/query_analysis_agent.py`)
**Purpose**: Parse and understand customer requests for intelligence on specific entities

**Capabilities**:
- Comprehensive entity recognition (persons, organizations, locations)
- Detailed classification with confidence scores
- Risk assessment and sensitivity analysis
- Information requirements extraction
- Collection strategy recommendations

**Key Features**:
- Enhanced entity extraction using multiple patterns
- Primary and secondary entity identification
- Context clue analysis and alias detection
- Complexity and sensitivity assessment
- Fallback analysis with pattern matching

### 2. Planning & Orchestration Agent (`agents/planning_agent.py`)
**Purpose**: Decompose queries into strategic information gathering tasks and coordinate agent activities

**Capabilities**:
- Multi-phase operation planning (Immediate → Development → Exploitation)
- Dynamic interview strategy development
- Agent coordination and task allocation
- Strategy adaptation based on collected intelligence
- Risk management and resource allocation

**Key Features**:
- Mission analysis with success criteria
- Phased collection strategies
- Interview approach optimization
- Real-time strategy updates
- Coordination between retrieval and pivot agents

### 3. Retrieval Agent (`agents/retrieval_agent.py`)
**Purpose**: Formulate targeted questions to gather specific evidence from the interviewer

**Capabilities**:
- Strategic question formulation based on investigation phases
- Multiple questioning techniques (open-ended, closed, hypothetical, timeline)
- Adaptive questioning based on pivot analysis
- Rapport management and sensitivity handling
- Priority-based question sequencing

**Key Features**:
- Context-aware question generation
- Pivot-adapted questioning strategies
- Tactical consideration integration
- Enhanced fallback questioning
- Strategic question prioritization

### 4. Pivot Agent (`agents/pivot_agent.py`)
**Purpose**: Analyze responses and identify new investigation angles, follow-up questions, and information gaps

**Capabilities**:
- Response credibility assessment
- New investigation angle identification
- Information gap analysis
- Evidence extraction and classification
- Strategic recommendation generation

**Key Features**:
- Intelligence value assessment
- Pivot opportunity identification
- Evidence extraction with confidence scoring
- Connection and pattern recognition
- Strategic redirection recommendations

### 5. Synthesis & Reporting Agent (`agents/synthesis_reporting_agent.py`)
**Purpose**: Aggregate collected intelligence into coherent narratives and generate structured reports

**Capabilities**:
- Large context window handling (up to 4M tokens)
- Comprehensive intelligence synthesis
- Structured report generation with confidence scores
- Pattern and connection analysis
- Strategic recommendation formulation

**Key Features**:
- Multi-source intelligence aggregation
- Entity profile generation
- Relationship mapping
- Gap analysis and recommendations
- Comprehensive evidence summarization

## Pipeline Flow

### Phase 1: Investigation Initialization
1. **Query Analysis**: Parse customer request and identify entities
2. **Strategic Planning**: Develop comprehensive investigation plan
3. **Initial Retrieval**: Formulate first set of targeted questions

### Phase 2: Iterative Intelligence Gathering
4. **User Response Processing**: Capture and analyze user responses
5. **Pivot Analysis**: Identify new angles and opportunities
6. **Strategy Update**: Adapt investigation strategy based on findings
7. **Adaptive Retrieval**: Generate follow-up questions based on pivot analysis

### Phase 3: Synthesis and Reporting
8. **Intelligence Synthesis**: Aggregate all collected intelligence
9. **Report Generation**: Create comprehensive structured reports
10. **Strategic Recommendations**: Provide actionable intelligence assessments

## Key Improvements

### Enhanced Entity Recognition
- Multi-pattern entity extraction
- Primary/secondary entity classification
- Confidence scoring and metadata tracking
- Alias and relationship detection

### Strategic Planning
- Multi-phase operation planning
- Dynamic strategy adaptation
- Agent coordination protocols
- Risk assessment and mitigation

### Iterative Intelligence Extraction
- Pivot-driven question adaptation
- Evidence-based strategy updates
- Confidence-weighted decision making
- Gap-focused information gathering

### Comprehensive Reporting
- Large context synthesis
- Structured intelligence reports
- Pattern and connection analysis
- Actionable recommendations

## Data Models

### Updated Schemas
- **EvidenceType**: Enhanced evidence classification
- **Entity**: Metadata support for complex entity information
- **InvestigationState**: Investigation focus tracking and metadata storage
- **IntelligenceReport**: Structured findings with confidence scores

### Agent Communication
- **AgentMessage**: Enhanced metadata support for agent coordination
- **Pipeline Orchestration**: Seamless agent-to-agent information flow
- **State Management**: Comprehensive investigation state tracking

## API Endpoints

### Core Intelligence Operations
- `POST /intelligence/investigate` - Start new investigation
- `POST /intelligence/{session_id}/respond` - Process user responses
- `GET /intelligence/{session_id}` - Get investigation status
- `GET /intelligence/{session_id}/report` - Generate comprehensive report
- `GET /intelligence/{session_id}/summary` - Get investigation summary

## Configuration and Deployment

### LLM Integration
- Google Gemini integration with search capabilities
- Configurable model selection
- Error handling and fallback mechanisms

### Service Architecture
- Modular agent design
- Centralized orchestration service
- Memory management and state persistence
- WebSocket support for real-time updates

## Usage Example

```python
# Start investigation
request = IntelligenceQueryRequest(
    query="Investigate John Smith's business activities in New York",
    priority="high"
)
state = await intelligence_service.start_investigation(request)

# Process responses iteratively
while state.status == InvestigationStatus.WAITING_FOR_INPUT:
    user_response = get_user_input()
    state = await intelligence_service.process_response(
        state.session_id, 
        user_response
    )

# Generate comprehensive report
report = await intelligence_service.generate_report(state.session_id)
```

## Benefits

1. **Strategic Intelligence Gathering**: Multi-phase approach maximizes information extraction
2. **Adaptive Questioning**: Pivot-driven strategy ensures optimal question formulation
3. **Comprehensive Analysis**: Large context synthesis provides complete intelligence picture
4. **Quality Assurance**: Confidence scoring and verification mechanisms ensure reliability
5. **Scalable Architecture**: Modular design supports easy extension and customization

This agent-based pipeline transforms the intelligence gathering process from simple Q&A into a sophisticated, strategic intelligence operation that maximizes information extraction while maintaining operational security and source protection. 