# Data Sleuth Agent Service

## Overview

The Data Sleuth Agent Service is an advanced AI-powered system designed to conduct investigations based on user queries. It utilizes a multi-agent architecture where different AI agents collaborate to analyze queries, plan investigation strategies, formulate targeted questions, and generate comprehensive reports. The system features a web-based user interface for interaction and a robust backend powered by FastAPI and various Large Language Models (LLMs).

## Key Features

-   **Multi-Agent Architecture:** Employs specialized AI agents for different stages of the intelligence gathering process (query analysis, planning, retrieval).
-   **LLM Integration:** Supports multiple LLM providers (OpenAI, Anthropic Claude, Google Gemini) for flexibility and leveraging different model strengths.
-   **Interactive Investigations:** Users can initiate investigations with a natural language query and provide follow-up responses.
-   **Dynamic PDF Report Generation:** Generates downloadable PDF reports summarizing the investigation, including executive summaries, key findings, entity profiles, intelligence gaps, recommendations, and conversation history.
-   **Web-Based UI:** A Flask-based frontend provides an intuitive interface for users to interact with the service.
-   **Configurable:** Settings, API keys, and model choices are managed through environment variables and configuration files.

## Technologies Used

-   **Backend:** Python, FastAPI, Uvicorn
-   **Frontend:** Python, Flask
-   **AI/LLM:**
    -   `google-generativeai` (for Gemini models)
    -   (Placeholders for OpenAI and Anthropic SDKs if fully implemented)
    -   LangChain (potentially, based on `requirements.txt`)
-   **PDF Generation:** `fpdf2`
-   **Configuration:** `pydantic-settings`, python-dotenv
-   **HTTP Client:** `requests`
-   **Core Python Libraries:** `logging`, `os`, `json`, `re`, `abc`

## Directory Structure

```
Intelligence_system/
├── api/                    # FastAPI routers and API endpoint definitions
│   └── routes/
├── agents/                 # Core AI agent implementations
│   ├── base_agent.py
│   ├── query_analysis_agent.py
│   ├── planning_agent.py
│   └── retrieval_agent.py
├── core/                   # Core application logic, configuration, logging
│   ├── config.py
│   └── logging_config.py
├── logs/                   # Log files (if configured to write to files)
├── models/                 # Pydantic models and schemas for data structures
├── services/               # Business logic services
│   ├── llm_providers.py    # Abstraction for LLM API interactions
│   ├── intelligence_service.py # Orchestrates the investigation workflow
│   └── websocket_manager.py  # Manages WebSocket connections
├── static/                 # Static files for the Flask frontend (CSS, JS, images)
├── templates/              # HTML templates for the Flask frontend
├── venv/                   # Python virtual environment (recommended)
├── .env                    # Environment variables (API keys, settings - create this manually)
├── app.py                  # Flask frontend application
├── main.py                 # FastAPI backend application
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup and Installation

### Prerequisites

-   Python 3.9+
-   `pip` (Python package installer)
-   Access to LLM APIs and corresponding API keys (Google Gemini, OpenAI, Anthropic)

### Installation Steps

1.  **Clone the Repository (if applicable):**
    If you're setting this up from a Git repository, clone it first.
    ```bash
    # git clone <repository_url>
    # cd Intelligence_system
    ```

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    python -m venv venv
    ```
    Activate it:
    -   Windows: `.\venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies:**
    Install all required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a `.env` file in the root of the `Intelligence_system` directory. This file will store your API keys and any custom configurations.
    Copy the following template into your `.env` file and replace the placeholder values with your actual API keys and desired settings:

    ```env
    # LLM API Keys
    OPENAI_API_KEY="sk-your_openai_api_key_here"
    ANTHROPIC_API_KEY="sk-ant-your_anthropic_api_key_here"
    GOOGLE_API_KEY="your_google_gemini_api_key_here"

    # Server Configuration (Optional - defaults are in core/config.py)
    # HOST="0.0.0.0"
    # PORT=8000
    # DEBUG=False # Set to True for Uvicorn auto-reload and debug logs

    # Model Configuration 
    # QUERY_ANALYSIS_MODEL=gemini-2.5-pro-preview-06-05" 
    # PLANNING_MODEL="gemini-2.5-pro-preview-06-05"
    # RETRIEVAL_MODEL="gemini-2.5-pro-preview-06-05"
    # SYNTHESIS_MODEL="gemini-2.5-pro-preview-06-05" # Not explicitly used yet, but planned

    # Logging Configuration (Optional)
    # LOG_LEVEL="INFO"
    ```
    **Note:** The application will function with only one API key if you intend to use only one type of LLM provider and configure the `*_MODEL` settings accordingly.

## Running the Application

You need to run the FastAPI backend and the Flask frontend separately, in two different terminal windows. Ensure your virtual environment is activated in both.

1.  **Start the FastAPI Backend Service:**
    Navigate to the `Intelligence_system` directory and run:
    ```bash
    python main.py
    ```
    By default, this will start the FastAPI service on `http://localhost:8000`. You should see log messages indicating the service has started.

2.  **Start the Flask Frontend Application:**
    In a new terminal, navigate to the `Intelligence_system` directory and run:
    ```bash
    python app.py
    ```
    By default, this will start the Flask application on `http://localhost:5000`.

3.  **Access the UI:**
    Open your web browser and go to `http://localhost:5000`. You should see the user interface of the Intelligence Gathering Service.

## Components

### FastAPI Backend (`main.py`)

-   **Description:** The core of the service, built with FastAPI. It handles API requests, orchestrates the agent-based investigation workflow, and interacts with LLM providers.
-   **Key Endpoints (prefixed with `/api/v1`):**
    -   `/health`: Checks the health of the service.
    -   `/intelligence/investigate` (POST): Initiates a new investigation with a user query.
    -   `/intelligence/{session_id}/respond` (POST): Allows users to provide follow-up responses to agent questions.
    -   `/intelligence/{session_id}/report` (GET): Retrieves the generated intelligence report data for a session.
    -   `/intelligence/ws/{session_id}` (WebSocket): For potential real-time communication (structure exists but full implementation might vary).
-   **Core Services:**
    -   `IntelligenceService`: Manages the lifecycle of an investigation, coordinating the different AI agents.
    -   `WebSocketManager`: Handles WebSocket connections if used for real-time updates.

### Flask Frontend (`app.py`)

-   **Description:** A simple web application built with Flask that provides the user interface for interacting with the intelligence service.
-   **Key Routes:**
    -   `/` (GET): Displays the main investigation interface.
    -   `/send_message` (POST): Sends the user's initial query or follow-up messages to the Flask app, which then forwards them to the FastAPI backend.
    -   `/generate_report` (POST): Triggers the display of report data in the UI and provides a link to download the PDF report.
    -   `/download_report/<session_id>` (GET): Dynamically generates and serves the PDF report for the specified session.

### LLM Providers (`services/llm_providers.py`)

-   **Description:** An abstraction layer for interacting with different Large Language Models. It defines a common `LLMProvider` interface and provides concrete implementations for:
    -   `OpenAIProvider` (for GPT models)
    -   `ClaudeProvider` (for Anthropic's Claude models)
    -   `GeminiProvider` (for Google's Gemini models)
-   A factory function `get_llm_provider(model_name)` instantiates the appropriate provider based on the model name specified in the configuration.

### Configuration (`core/config.py` & `.env`)

-   **`core/config.py`:** Uses `pydantic-settings` to define and load application settings. It specifies default values for server configuration, API keys (though primarily loaded from `.env`), model names for different tasks, and logging settings.
-   **`.env` file:** (User-created) Stores sensitive API keys and allows overriding default settings defined in `config.py`.

### Logging (`core/logging_config.py`)

-   Sets up standardized logging for the application, including log levels, formats, and handlers (console and file).
-   Allows suppressing verbose logs from external libraries like `httpx`, `openai`, and `watchfiles`.

## AI Agents (`agents/`)

The system employs a multi-agent architecture where each agent has a specialized role:

### 1. `BaseAgent` (`base_agent.py`)

-   **Description:** An abstract base class that provides common functionalities for all specialized agents, including initialization with an LLM provider, a system prompt, and methods for generating LLM responses and creating standardized agent messages.

### 2. `QueryAnalysisAgent` (`query_analysis_agent.py`)

-   **Role:** The first agent to process a user's request.
-   **Functionality:**
    -   Parses the initial user query.
    -   Identifies key target entities (persons, organizations, locations).
    -   Determines information types requested, investigation objectives, and potential angles.
    -   Assesses query complexity.
    -   Outputs its analysis in a structured format (attempts JSON, with fallback).
-   **System Prompt Focus:** "Expert intelligence analyst specializing in query decomposition."

### 3. `PlanningOrchestrationAgent` (`planning_agent.py`)

-   **Role:** Develops the strategic approach for the investigation based on the query analysis.
-   **Functionality:**
    -   Creates a comprehensive investigation plan.
    -   Defines information gathering priorities.
    -   Suggests question strategies and follow-up angles.
    -   Identifies initial information gaps.
-   **System Prompt Focus:** "Master intelligence strategist... Think like a seasoned intelligence officer planning an operation."

### 4. `RetrievalAgent` (also known as "Inspector Data-seau") (`retrieval_agent.py`)

-   **Role:** Formulates targeted questions to gather intelligence and fill identified gaps. This agent interacts (indirectly via the user) to elicit information.
-   **Functionality:**
    -   Builds context from existing target entities and evidence.
    -   Formulates 2-3 strategic questions at a time based on current information gaps.
    -   Frames questions in a charming and persistent style to maximize information extraction.
-   **System Prompt Focus:** "Expert interrogator with a charming but persistent style... Your questions should be direct but not obvious, strategic but natural."

## Key Functionalities Explained

1.  **Initiate Investigation:** The user starts by typing a query into the web UI. This is sent to the Flask app, then to the FastAPI `/investigate` endpoint.
2.  **Agent Workflow (Simplified):**
    -   The `IntelligenceService` receives the query.
    -   **Query Analysis Agent** processes the query to identify entities and objectives.
    -   **Planning & Orchestration Agent** creates an investigation plan and identifies initial information gaps.
    -   **Retrieval Agent** formulates initial strategic questions based on the plan and gaps. These questions are sent back to the user.
3.  **User Interaction:** The user provides answers/responses to the agent's questions. These are sent via the `/respond` endpoint.
4.  **Iterative Process:** The Retrieval Agent (and potentially others in a more complex setup) would then process these responses, update the investigation state, and potentially formulate new questions, continuing the cycle until sufficient information is gathered or the investigation objectives are met. (The current implementation focuses on the initial questioning phase after planning).
5.  **Report Generation:**
    -   The user can request a report via the UI.
    -   Flask's `/generate_report` endpoint calls FastAPI's `/report` endpoint.
    -   FastAPI's `/report` endpoint compiles the `IntelligenceReport` model with data like executive summary, key findings, entity profiles, etc., based on the current `InvestigationState`.
    -   Flask's `/download_report/<session_id>` endpoint fetches this report data again and uses `fpdf2` to dynamically generate a PDF containing these details, which is then served to the user for download.

## Potential Future Enhancements

-   Deeper evidence analysis and correlation by a dedicated "Synthesis Agent."
-   More sophisticated state management and iterative looping in the agent workflow.
-   Full implementation of WebSocket for real-time UI updates during agent processing.
-   Integration with external data sources for automated evidence retrieval.
-   More advanced error handling and user feedback mechanisms.

---

This README provides a comprehensive starting point. You can expand it further as the project evolves. 