from flask import Flask, render_template, jsonify, request, session, make_response, send_file
import requests # Added
import os
import logging # Added for better logging
from fpdf import FPDF
from fpdf.errors import FPDFException # Added FPDFException import
from io import BytesIO # Added BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24) # Added: Important for session management

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FASTAPI_BASE_URL = "http://localhost:8000/api/v1/intelligence" # Added

def format_fastapi_response_for_ui(investigation_state: dict) -> tuple[str, str, list, int]:
    """
    Formats the InvestigationState from FastAPI for the UI.
    Returns: (system_message, agent_status_text, key_facts, progress_percentage)
    """
    system_message = "No new messages from the agent."
    if investigation_state.get("current_questions"):
        system_message = "\n".join(investigation_state["current_questions"])
    elif investigation_state.get("conversation_history"):
        # Get the last message from the agent
        agent_messages = [
            msg for msg in investigation_state["conversation_history"] 
            if msg.get("agent_name") != "User" # Assuming user messages might also be logged
        ]
        if agent_messages:
            system_message = agent_messages[-1].get("message", system_message)

    status_map = {
        "PENDING": "Pending Investigation",
        "IN_PROGRESS": "Investigation in Progress",
        "WAITING_FOR_INPUT": "Waiting for Your Input",
        "COMPLETED": "Investigation Complete",
        "FAILED": "Investigation Failed"
    }
    agent_status_text = status_map.get(investigation_state.get("status", "UNKNOWN").upper(), "Unknown Status")

    key_facts = []
    
    # Extract target entities with enhanced details
    if investigation_state.get("target_entities"):
        for entity in investigation_state["target_entities"]:
            entity_name = entity.get('name', 'N/A')
            entity_type = entity.get('entity_type', 'N/A')
            priority = entity.get('priority', 'medium')
            confidence = entity.get('confidence_score', 0.0)
            
            # Create more informative entity fact
            entity_fact = f"🎯 Target: {entity_name} ({entity_type}) - Priority: {priority}, Confidence: {confidence:.1f}"
            key_facts.append(entity_fact)
            
            # Add metadata details if available
            metadata = entity.get('metadata', {})
            if metadata:
                for key, value in metadata.items():
                    if key in ['context_clues', 'potential_aliases'] and value:
                        if isinstance(value, list):
                            key_facts.append(f"   📝 {key.replace('_', ' ').title()}: {', '.join(value[:2])}")
                        else:
                            key_facts.append(f"   📝 {key.replace('_', ' ').title()}: {value}")

    # Extract evidence with intelligence value
    if investigation_state.get("evidence_pool"):
        evidence_pool = investigation_state["evidence_pool"]
        
        # Show high-confidence evidence
        high_confidence_evidence = [e for e in evidence_pool if e.get('confidence_score', 0) > 0.7]
        for evidence in high_confidence_evidence[:3]:  # Top 3 high-confidence items
            content = evidence.get('content', 'N/A')
            confidence = evidence.get('confidence_score', 0.0)
            evidence_type = evidence.get('evidence_type', 'unknown')
            
            # Truncate long content
            if len(content) > 60:
                content = content[:60] + "..."
            
            key_facts.append(f"🔍 Evidence ({evidence_type}): {content} (Confidence: {confidence:.1f})")
        
        # Add evidence summary
        if len(evidence_pool) > 3:
            key_facts.append(f"📊 Total Evidence Collected: {len(evidence_pool)} items")

    # Extract key insights from agent messages
    if investigation_state.get("conversation_history"):
        for msg in investigation_state["conversation_history"]:
            agent_name = msg.get("agent_name", "")
            message_type = msg.get("message_type", "")
            metadata = msg.get("metadata", {})
            
            # Extract insights from pivot agent analysis
            if agent_name == "Pivot Agent" and message_type == "analysis":
                if metadata.get("new_angles_count", 0) > 0:
                    key_facts.append(f"🔄 New Investigation Angles: {metadata['new_angles_count']} identified")
                if metadata.get("evidence_extracted", 0) > 0:
                    key_facts.append(f"📈 Evidence Extracted: {metadata['evidence_extracted']} new items")
            
            # Extract insights from query analysis
            elif agent_name == "Query Analysis Agent" and message_type == "analysis":
                if metadata.get("complexity"):
                    key_facts.append(f"🎯 Investigation Complexity: {metadata['complexity'].title()}")
                if metadata.get("primary_entities", 0) > 0:
                    key_facts.append(f"👥 Primary Entities: {metadata['primary_entities']} identified")
            
            # Extract insights from planning agent
            elif agent_name == "Planning & Orchestration Agent" and message_type == "planning":
                if metadata.get("current_phase"):
                    key_facts.append(f"📋 Investigation Phase: {metadata['current_phase'].title()}")
                if metadata.get("objectives_count", 0) > 0:
                    key_facts.append(f"🎯 Strategic Objectives: {metadata['objectives_count']} defined")

    # Extract investigation focus areas
    if investigation_state.get("investigation_focus"):
        focus_areas = investigation_state["investigation_focus"][:2]  # Top 2 focus areas
        if focus_areas:
            key_facts.append(f"🎯 Current Focus: {', '.join(focus_areas)}")

    # Extract information gaps
    if investigation_state.get("information_gaps"):
        gaps_count = len(investigation_state["information_gaps"])
        if gaps_count > 0:
            key_facts.append(f"❓ Information Gaps: {gaps_count} areas need investigation")

    # Add investigation metadata insights
    metadata = investigation_state.get("metadata", {})
    if metadata:
        if metadata.get("sensitivity_level"):
            key_facts.append(f"🔒 Sensitivity Level: {metadata['sensitivity_level'].title()}")
        
        if metadata.get("current_phase"):
            phase_status = metadata.get("phase_status", "on_track")
            key_facts.append(f"📊 Phase Status: {phase_status.replace('_', ' ').title()}")

    # Ensure we have at least some basic facts
    if not key_facts:
        key_facts = ["🔍 Investigation initialized", "⏳ Awaiting intelligence gathering"]

    # Calculate comprehensive progress based on multiple factors
    progress_percentage = calculate_investigation_progress(investigation_state)

    return system_message, agent_status_text, key_facts, progress_percentage

def calculate_investigation_progress(investigation_state: dict) -> int:
    """Calculate investigation progress based on multiple factors"""
    progress_factors = []
    
    # Factor 1: Entity identification (0-25%)
    entities = investigation_state.get("target_entities", [])
    if entities:
        entity_progress = min(25, len(entities) * 8)  # Up to 25% for 3+ entities
        progress_factors.append(entity_progress)
        logger.debug(f"Entity progress: {entity_progress}% ({len(entities)} entities)")
    
    # Factor 2: Evidence collection (0-35%)
    evidence_pool = investigation_state.get("evidence_pool", [])
    if evidence_pool:
        evidence_progress = min(35, len(evidence_pool) * 7)  # Up to 35% for 5+ evidence items
        progress_factors.append(evidence_progress)
        logger.debug(f"Evidence progress: {evidence_progress}% ({len(evidence_pool)} evidence items)")
    
    # Factor 3: Conversation depth (0-20%)
    conversation_history = investigation_state.get("conversation_history", [])
    user_responses = [msg for msg in conversation_history if msg.get("agent_name") == "User"]
    if user_responses:
        conversation_progress = min(20, len(user_responses) * 4)  # Up to 20% for 5+ exchanges
        progress_factors.append(conversation_progress)
        logger.debug(f"Conversation progress: {conversation_progress}% ({len(user_responses)} user responses)")
    
    # Factor 4: Agent analysis completion (0-15%)
    agent_messages = [msg for msg in conversation_history if msg.get("agent_name") != "User"]
    analysis_types = set()
    for msg in agent_messages:
        if msg.get("message_type") in ["analysis", "planning", "adaptation"]:
            analysis_types.add(msg.get("agent_name", ""))
    
    if analysis_types:
        analysis_progress = min(15, len(analysis_types) * 5)  # Up to 15% for 3+ agent types
        progress_factors.append(analysis_progress)
        logger.debug(f"Analysis progress: {analysis_progress}% ({len(analysis_types)} agent types)")
    
    # Factor 5: Investigation phase advancement (0-5%)
    metadata = investigation_state.get("metadata", {})
    current_phase = metadata.get("current_phase", "immediate")
    phase_progress = 0
    if current_phase == "development":
        phase_progress = 3
    elif current_phase == "exploitation":
        phase_progress = 5
    
    if phase_progress > 0:
        progress_factors.append(phase_progress)
        logger.debug(f"Phase progress: {phase_progress}% (phase: {current_phase})")
    
    # Calculate total progress
    total_progress = sum(progress_factors)
    
    # Add confidence score bonus (0-10%)
    confidence_score = investigation_state.get("confidence_score", 0.0)
    confidence_bonus = int(confidence_score * 10)
    total_progress += confidence_bonus
    
    # Ensure progress is between 0 and 100
    final_progress = min(100, max(0, total_progress))
    
    logger.info(f"Progress calculation: {final_progress}% (factors: {progress_factors}, confidence bonus: {confidence_bonus}%)")
    
    return final_progress

@app.route('/')
def index():
    session.pop('session_id', None) # Clear previous session_id on new visit
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    session_id = session.get('session_id')

    system_response_text = "Could not process your request."
    agent_status = "Error"
    ui_key_facts = []
    ui_progress = 0

    try:
        if not session_id:
            # Initial query: Start a new investigation
            logger.info(f"Starting new investigation with query: {user_message}")
            payload = {"query": user_message, "priority": "medium"} # IntelligenceQueryRequest
            response = requests.post(f"{FASTAPI_BASE_URL}/investigate", json=payload, timeout=900)
            response.raise_for_status()
            investigation_state = response.json()
            
            session['session_id'] = investigation_state.get('session_id')
            if not session['session_id']:
                raise ValueError("FastAPI did not return a session_id.")
            logger.info(f"Investigation started. Session ID: {session['session_id']}")
            
            system_response_text, agent_status, ui_key_facts, ui_progress = format_fastapi_response_for_ui(investigation_state)

        else:
            # Follow-up message: Respond to existing investigation
            logger.info(f"Sending response for session {session_id}: {user_message}")
            payload = {"response": user_message} # Body for /respond endpoint
            response = requests.post(f"{FASTAPI_BASE_URL}/{session_id}/respond", json=payload, timeout=900)
            response.raise_for_status()
            investigation_state = response.json()
            logger.info(f"Response processed for session {session_id}.")
            
            system_response_text, agent_status, ui_key_facts, ui_progress = format_fastapi_response_for_ui(investigation_state)

    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI connection error: {e}")
        system_response_text = f"Error communicating with the intelligence service: {e}"
        session.pop('session_id', None) # Clear session on error
    except ValueError as e:
        logger.error(f"Data processing error: {e}")
        system_response_text = f"Error processing data: {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred in /send_message: {e}", exc_info=True)
        system_response_text = f"An unexpected server error occurred."

    return jsonify({
        'response': system_response_text, 
        'agent_status': agent_status,
        'key_facts': ui_key_facts, # Added for UI
        'progress': ui_progress    # Added for UI
    })

@app.route('/generate_report', methods=['POST'])
def generate_report():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'No active investigation session found.'}), 400

    logger.info(f"Generating report for session {session_id}")
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/{session_id}/report", timeout=60)
        response.raise_for_status()
        report_data_from_fastapi = response.json() # IntelligenceReport model

        # Adapt FastAPI report data to the UI's expected format
        ui_report_data = {
            'title': f"Intelligence Report - Session {report_data_from_fastapi.get('session_id', 'N/A')}",
            'summary': report_data_from_fastapi.get('executive_summary', 'No summary available.'),
            'key_findings': report_data_from_fastapi.get('key_findings', []),
            # Update the download_link to point to the new dynamic endpoint
            'download_link': f'/download_report/{session_id}'
        }
        logger.info(f"Report data prepared for UI: {ui_report_data.get('title')}")
        logger.info(f"Report generated successfully for session {session_id}")
        return jsonify({
            'status': 'success', 
            'message': 'Report generated successfully from FastAPI.', 
            'report_data': ui_report_data, 
            'agent_status': 'Report Ready'
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI connection error during report generation: {e}")
        return jsonify({'status': 'error', 'message': f"Error generating report: {e}", 'agent_status': 'Error Generating Report'}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred in /generate_report: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An unexpected server error occurred while generating the report.', 'agent_status': 'Error Generating Report'}), 500

@app.route('/download_report/<session_id>', methods=['GET'])
def download_report(session_id: str):
    logger.info(f"Attempting to download report for session_id: {session_id}")
    try:
        # 1. Fetch report data from FastAPI
        fastapi_report_url = f"{FASTAPI_BASE_URL}/{session_id}/report"
        response = requests.get(fastapi_report_url, timeout=60)
        response.raise_for_status() # Will raise an exception for HTTP error codes
        report_data = response.json()
        logger.info(f"Successfully fetched report data from FastAPI for session {session_id}")

        # 2. Generate PDF using fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Intelligence Report", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Session ID: {report_data.get('session_id', 'N/A')}", ln=True, align="C")
        pdf.ln(10)

        # Executive Summary
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", "", 12)
        summary = report_data.get('executive_summary', 'No summary available.')
        # Pass string directly to multi_cell, relying on FPDF's UTF-8 handling
        pdf.multi_cell(0, 10, summary)
        pdf.ln(5)

        # Key Findings
        key_findings = report_data.get('key_findings', [])
        if key_findings:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Key Findings", ln=True)
            pdf.set_font("Arial", "", 12)
            for i, finding in enumerate(key_findings):
                finding_text = f"{i+1}. {finding}"
                pdf.multi_cell(0, 10, finding_text)
                pdf.ln(2) # Add a little space between findings
        pdf.ln(5) # Space after Key Findings section

        # Entity Profiles
        entity_profiles = report_data.get('entity_profiles', [])
        if entity_profiles:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Target Entity Profiles", ln=True)
            pdf.set_font("Arial", "", 12)
            for entity in entity_profiles:
                entity_name = entity.get('name', 'N/A')
                entity_type = entity.get('type', 'N/A')
                profile_text = f"- Name: {entity_name}, Type: {entity_type}"
                pdf.multi_cell(0, 10, profile_text)
                pdf.ln(1)
            pdf.ln(5)

        # Intelligence Gaps
        intelligence_gaps = report_data.get('intelligence_gaps', [])
        if intelligence_gaps:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Identified Intelligence Gaps", ln=True)
            pdf.set_font("Arial", "", 12)
            for i, gap in enumerate(intelligence_gaps):
                gap_text = f"- {gap}"
                pdf.multi_cell(0, 10, gap_text)
                pdf.ln(1)
            pdf.ln(5)

        # Recommendations
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Recommendations", ln=True)
            pdf.set_font("Arial", "", 12)
            for i, rec in enumerate(recommendations):
                rec_text = f"- {rec}"
                pdf.multi_cell(0, 10, rec_text)
                pdf.ln(1)
            pdf.ln(5)

        # Assessment & Metadata
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Assessment & Metadata", ln=True)
        pdf.set_font("Arial", "", 12)

        confidence = report_data.get('confidence_assessment', {})
        overall_confidence = confidence.get('overall', 'N/A')
        if isinstance(overall_confidence, (float, int)):
            overall_confidence_text = f"Overall Confidence Score: {overall_confidence*100:.2f}%"
        else:
            overall_confidence_text = f"Overall Confidence Score: {overall_confidence}"
        pdf.multi_cell(0, 10, overall_confidence_text)
        pdf.ln(1)

        evidence_count = report_data.get('evidence_count', 'N/A')
        evidence_text = f"Total Evidence Items: {evidence_count}"
        pdf.multi_cell(0, 10, evidence_text)
        pdf.ln(1)

        generated_at = report_data.get('generated_at', 'N/A')
        generated_at_text = f"Report Generated At: {generated_at}"
        pdf.multi_cell(0, 10, generated_at_text)
        pdf.ln(5)

        # Conversation History
        conversation_history = report_data.get('conversation_history', [])
        if conversation_history:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Conversation History", ln=True)
            pdf.set_font("Arial", "", 10) # Smaller font for conversation
            for i, entry in enumerate(conversation_history):
                speaker = entry.get('agent_name', 'Unknown') # This captures the speaker, whether it's 'User', 'System', or a specific agent
                message = entry.get('message', '')
                timestamp = entry.get('timestamp', '') 
                
                # Speaker and Timestamp (if available)
                header_text = f"{speaker}"
                if timestamp:
                    # Attempt to format timestamp if it's a parseable string, otherwise use as is
                    try:
                        # Example: format if timestamp is like "2023-10-27T10:30:00"
                        from datetime import datetime
                        dt_obj = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_ts = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                        header_text += f" ({formatted_ts})"
                    except (ValueError, TypeError):
                        header_text += f" ({timestamp})" # Use as is if not standard ISO
                
                pdf.set_font("Arial", "B", 10)
                pdf.multi_cell(0, 5, header_text, ln=1) # Use ln=1 to move to next line, left margin
                
                # Message content
                pdf.set_font("Arial", "", 10)
                try:
                    # Sanitize message for FPDF standard font encoding
                    sanitized_message = message.encode('latin-1', 'replace').decode('latin-1')
                    # Use w=0 for full available width from current X (should be left margin) to right margin
                    pdf.multi_cell(0, 5, sanitized_message)
                except FPDFException as fpdf_e:
                    if "Not enough horizontal space" in str(fpdf_e):
                        # Log current PDF state at the point of original message failure
                        pdf_state_on_error = f"PDF state: X={pdf.x:.2f}, Y={pdf.y:.2f}, PageWidth={pdf.w:.2f}, LeftMargin={pdf.l_margin:.2f}, RightMargin={pdf.r_margin:.2f}, PageHeight={pdf.h:.2f}, TopMargin={pdf.t_margin:.2f}, BottomMargin={pdf.b_margin:.2f}"
                        logger.warning(f"FPDFException for session {session_id} rendering message: {fpdf_e}. {pdf_state_on_error}. Problematic message (first 200 chars): '{message[:200]}...'", exc_info=True)
                        
                        # Move to a new line and reset X position before attempting placeholder
                        pdf.ln(5) # Ensure we are on a new line, use a reasonable height
                        pdf.set_x(pdf.l_margin) # Reset X to the left margin
                        try:
                            pdf.multi_cell(0, 5, "[Message too wide/unrenderable]") # Simplified placeholder, w=0 for full width
                        except FPDFException as placeholder_fpdf_e:
                            logger.error(f"FPDFException even for placeholder in session {session_id}: {placeholder_fpdf_e}. Placeholder PDF state: X={pdf.x:.2f}, Y={pdf.y:.2f}", exc_info=True)
                            pass 
                    else:
                        raise # Re-raise other FPDFExceptions
                pdf.ln(3) # Space between messages
            pdf.ln(5)
        else:
            pdf.set_font("Arial", "I", 12) 
            pdf.multi_cell(0, 10, "(Conversation history not available in this report extract)")
            pdf.ln(5)
        
        # 3. Prepare PDF for sending
        pdf_buffer = BytesIO()
        # FPDF.output writes to a file-like object if 'F' or 'S' is not specified as dest for BytesIO
        # However, to be explicit and ensure it works with BytesIO as a file:
        # pdf.output(pdf_buffer, 'F') # This attempts to write to a file *named* by the buffer
        # For BytesIO, usually we get the bytes and then write them or use them.
        # Let's get the output as bytes:
        pdf_output_bytes = pdf.output(dest='S') # Removed .encode('latin-1')
        pdf_buffer.write(pdf_output_bytes)
        pdf_buffer.seek(0)
        
        logger.info(f"PDF generated successfully for session {session_id}. Size: {len(pdf_output_bytes)} bytes")

        # 4. Send the PDF as a file download
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'report_{session_id}.pdf',
            mimetype='application/pdf'
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI connection error during PDF generation for session {session_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Could not fetch report data: {e}"}), 500
    except Exception as e:
        logger.error(f"Error generating or sending PDF for session {session_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Could not generate PDF report."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 