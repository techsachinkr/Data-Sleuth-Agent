# Data Sleuth Agent - Advanced Intelligence Gathering System

## Overview

The Data Sleuth Agent is a sophisticated AI-powered intelligence gathering system that employs a **7-phase agent-based pipeline** to conduct comprehensive investigations. The system features specialized AI agents that collaborate to analyze queries, plan strategic investigations, gather intelligence through iterative questioning, and generate detailed reports with confidence scoring and real-time progress tracking.

## 🚀 Key Features

### **Advanced Agent Pipeline**
- **7-Phase Investigation Process**: Query Analysis → Planning → Initial Retrieval → Pivot Analysis → Strategy Update → Adaptive Retrieval → Synthesis & Reporting
- **5 Specialized AI Agents**: Each with distinct roles and capabilities
- **Real-time Progress Tracking**: Multi-factor progress calculation with visual feedback
- **Adaptive Intelligence Gathering**: Dynamic strategy updates based on collected evidence

### **Intelligence Capabilities**
- **Entity Recognition & Analysis**: Advanced entity extraction with confidence scoring
- **Evidence Collection & Classification**: Structured evidence gathering with intelligence value assessment
- **Strategic Question Formulation**: Context-aware, pivot-driven questioning strategies
- **Large Context Synthesis**: Handle up to 4M+ tokens for comprehensive analysis
- **Confidence-Weighted Reporting**: All findings include reliability assessments

### **User Experience**
- **Interactive Web Interface**: Real-time key facts, progress tracking, and agent status updates
- **Dynamic PDF Report Generation**: Comprehensive reports with executive summaries and strategic recommendations
- **Session Management**: Persistent investigation sessions with state tracking
- **Visual Progress Indicators**: Color-coded progress bars with smooth transitions

## 🏗️ System Architecture

### **Multi-Agent Pipeline**

#### **1. Query Analysis Agent** 🔍
- **Purpose**: Parse customer requests and identify intelligence targets
- **Capabilities**:
  - Advanced entity recognition (persons, organizations, locations, projects)
  - Risk assessment and sensitivity analysis
  - Primary/secondary entity classification
  - Context clue analysis and alias detection
  - Complexity assessment with confidence scoring

#### **2. Planning & Orchestration Agent** 📋
- **Purpose**: Develop strategic investigation plans and coordinate agent activities
- **Capabilities**:
  - Multi-phase operation planning (Immediate → Development → Exploitation)
  - Dynamic interview strategy development
  - Agent coordination and task allocation
  - Risk management and resource allocation
  - Real-time strategy adaptation

#### **3. Retrieval Agent** 🕵️
- **Purpose**: Formulate targeted questions to extract specific intelligence
- **Capabilities**:
  - Strategic question formulation based on investigation phases
  - Multiple questioning techniques (open-ended, closed, hypothetical, timeline)
  - Adaptive questioning based on pivot analysis
  - Rapport management and sensitivity handling
  - Priority-based question sequencing

#### **4. Pivot Agent** 🔄
- **Purpose**: Analyze responses and identify new investigation angles
- **Capabilities**:
  - Response credibility assessment
  - New investigation angle identification
  - Information gap analysis
  - Evidence extraction and classification
  - Strategic recommendation generation

#### **5. Synthesis & Reporting Agent** 📊
- **Purpose**: Aggregate intelligence into coherent narratives and structured reports
- **Capabilities**:
  - Large context window handling (4M+ tokens)
  - Comprehensive intelligence synthesis
  - Structured report generation with confidence scores
  - Pattern and connection analysis
  - Strategic recommendation formulation

## 🔄 7-Phase Investigation Pipeline

### **Phase 1-3: Investigation Initialization**
1. **Query Analysis**: Parse request and identify target entities
2. **Strategic Planning**: Develop comprehensive investigation plan
3. **Initial Retrieval**: Formulate first set of targeted questions

### **Phase 4-6: Iterative Intelligence Gathering**
4. **User Response Processing**: Capture and analyze user responses
5. **Pivot Analysis**: Identify new angles and opportunities
6. **Strategy Update**: Adapt investigation strategy based on findings

### **Phase 7: Synthesis and Reporting**
7. **Adaptive Retrieval**: Generate follow-up questions based on pivot analysis
8. **Intelligence Synthesis**: Aggregate all collected intelligence
9. **Report Generation**: Create comprehensive structured reports

## 📊 Progress Tracking System

The system features a sophisticated progress calculation based on multiple factors:

- **Entity Identification** (0-25%): Progress based on target entities identified
- **Evidence Collection** (0-35%): Progress based on evidence items gathered
- **Conversation Depth** (0-20%): Progress based on user interaction depth
- **Agent Analysis** (0-15%): Progress based on different agent analyses completed
- **Investigation Phase** (0-5%): Bonus for advancing through investigation phases
- **Confidence Bonus** (0-10%): Additional progress based on overall confidence score

## 🛠️ Technologies Used

### **Backend**
- **FastAPI**: High-performance API framework with async support
- **Python 3.9+**: Core application language
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

### **Frontend**
- **Flask**: Web application framework for UI
- **JavaScript**: Real-time UI updates and progress tracking
- **HTML/CSS**: Modern, responsive user interface
- **FPDF2**: Dynamic PDF report generation

### **AI/LLM Integration**
- **Google Gemini**: Primary LLM provider with search capabilities
- **OpenAI GPT**: Alternative LLM provider (configurable)
- **Anthropic Claude**: Alternative LLM provider (configurable)
- **Custom LLM Abstraction**: Unified interface for multiple providers

### **Data Management**
- **Memory Manager**: Efficient conversation and state management
- **WebSocket Manager**: Real-time communication support
- **Session Management**: Persistent investigation sessions

## 📁 Directory Structure

```
Data-Sleuth-Agent/
├── agents/                     # AI Agent Implementations
│   ├── base_agent.py          # Abstract base class for all agents
│   ├── query_analysis_agent.py # Query parsing and entity recognition
│   ├── planning_agent.py      # Strategic planning and orchestration
│   ├── retrieval_agent.py     # Question formulation and intelligence gathering
│   ├── pivot_agent.py         # Response analysis and angle identification
│   └── synthesis_reporting_agent.py # Intelligence synthesis and reporting
├── api/                       # FastAPI Routes and Endpoints
│   └── routes/
│       └── intelligence.py   # Intelligence gathering API endpoints
├── core/                      # Core Application Logic
│   ├── config.py             # Configuration management
│   └── logging_config.py     # Logging setup and configuration
├── models/                    # Data Models and Schemas
│   └── schemas.py            # Pydantic models for data structures
├── services/                  # Business Logic Services
│   ├── intelligence_service.py # Main orchestration service
│   ├── llm_providers.py      # LLM provider abstraction
│   ├── websocket_manager.py  # WebSocket connection management
│   └── memory_manager.py     # Memory and state management
├── static/                    # Frontend Static Files
│   ├── css/style.css         # Styling with progress indicators
│   └── js/script.js          # Real-time UI updates and interactions
├── templates/                 # HTML Templates
│   └── index.html            # Main investigation interface
├── logs/                      # Application Logs
├── venv/                      # Python Virtual Environment
├── .env                       # Environment Variables (create manually)
├── .gitignore                # Git ignore rules
├── app.py                     # Flask Frontend Application
├── main.py                    # FastAPI Backend Application
├── requirements.txt           # Python Dependencies
├── AGENT_PIPELINE_OVERVIEW.md # Detailed agent architecture documentation
└── README.md                  # This file
```

## 🚀 Setup and Installation

### Prerequisites

- **Python 3.9+** with pip
- **API Keys** for LLM providers:
  - Google Gemini API key (primary)
  - OpenAI API key (optional)
  - Anthropic API key (optional)

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd Data-Sleuth-Agent
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   ```
   
   **Activate:**
   - Windows: `.\venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # LLM API Keys
   GOOGLE_API_KEY="your_google_gemini_api_key_here"
   OPENAI_API_KEY="sk-your_openai_api_key_here"  # Optional
   ANTHROPIC_API_KEY="sk-ant-your_anthropic_api_key_here"  # Optional

   # Server Configuration
   HOST="0.0.0.0"
   PORT=8000
   DEBUG=False

   # Model Configuration
   QUERY_ANALYSIS_MODEL="gemini-2.0-flash-exp"
   PLANNING_MODEL="gemini-2.0-flash-exp"
   RETRIEVAL_MODEL="gemini-2.0-flash-exp"
   PIVOT_MODEL="gemini-2.0-flash-exp"
   SYNTHESIS_MODEL="gemini-2.0-flash-exp"

   # Logging Configuration
   LOG_LEVEL="INFO"
   ```

## 🏃 Running the Application

### Start Both Services

1. **Start FastAPI Backend:**
   ```bash
   python main.py
   ```
   Backend runs on: `http://localhost:8000`

2. **Start Flask Frontend (new terminal):**
   ```bash
   python app.py
   ```
   Frontend runs on: `http://localhost:5000`

3. **Access the Application:**
   Open your browser to: `http://localhost:5000`

## 🔧 API Endpoints

### **Core Intelligence Operations**
- `POST /api/v1/intelligence/investigate` - Start new investigation
- `POST /api/v1/intelligence/{session_id}/respond` - Process user responses
- `GET /api/v1/intelligence/{session_id}` - Get investigation status
- `GET /api/v1/intelligence/{session_id}/report` - Generate comprehensive report
- `GET /api/v1/intelligence/health` - Service health check

### **Frontend Routes**
- `GET /` - Main investigation interface
- `POST /send_message` - Send user messages to backend
- `POST /generate_report` - Trigger report generation
- `GET /download_report/<session_id>` - Download PDF report

## 💡 Usage Example

### **Starting an Investigation**
```python
# API Request
POST /api/v1/intelligence/investigate
{
    "query": "Investigate John Smith's business activities in New York",
    "priority": "high"
}

# Response includes session_id and initial questions
```

### **Interactive Investigation Flow**
1. **User submits initial query** → System analyzes and plans investigation
2. **Agent asks strategic questions** → User provides responses
3. **System adapts strategy** → Pivot agent identifies new angles
4. **Continued questioning** → Evidence collection and analysis
5. **Report generation** → Comprehensive intelligence report with confidence scores

## 🎯 Key Functionalities

### **Real-Time Features**
- **Progress Tracking**: Visual progress bar with multi-factor calculation
- **Key Facts Display**: Real-time updates of investigation findings
- **Agent Status**: Current agent activity and investigation phase
- **Evidence Collection**: Structured evidence gathering with confidence scores

### **Intelligence Analysis**
- **Entity Profiling**: Comprehensive entity analysis with metadata
- **Relationship Mapping**: Connection analysis between entities
- **Evidence Classification**: Structured evidence categorization
- **Confidence Scoring**: Reliability assessment for all findings

### **Report Generation**
- **Executive Summaries**: High-level intelligence assessments
- **Key Findings**: Structured findings with confidence scores
- **Entity Profiles**: Detailed target entity information
- **Strategic Recommendations**: Actionable intelligence insights
- **PDF Export**: Professional report formatting

## 🔮 Advanced Features

### **Memory Management**
- Efficient conversation history tracking
- State persistence across sessions
- Large context window handling

### **Adaptive Intelligence**
- Dynamic strategy updates based on collected evidence
- Pivot-driven question adaptation
- Confidence-weighted decision making

### **Quality Assurance**
- Multi-agent verification processes
- Confidence scoring for all findings
- Evidence credibility assessment

## 🚀 Future Enhancements

- **External Data Integration**: Automated evidence retrieval from external sources
- **Advanced Analytics**: Pattern recognition and predictive analysis
- **Multi-language Support**: International intelligence gathering capabilities
- **API Integrations**: Third-party intelligence service connections
- **Advanced Visualization**: Interactive relationship and timeline visualizations

---

## 📖 Additional Documentation

- **[Agent Pipeline Overview](AGENT_PIPELINE_OVERVIEW.md)**: Detailed agent architecture and capabilities
- **API Documentation**: Available at `http://localhost:8000/docs` when running
- **Configuration Guide**: See `core/config.py` for all configuration options

---

**Data Sleuth Agent** - Transforming intelligence gathering through advanced AI agent collaboration. 