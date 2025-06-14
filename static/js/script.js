// Client-side JavaScript for UI interactions

document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messageDisplay = document.getElementById('message-display');
    const generateReportButton = document.getElementById('generate-report-button');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const keyFactsList = document.getElementById('key-facts-list');
    const agentStatus = document.getElementById('agent-status');
    const reportOutput = document.getElementById('report-output');

    // Function to add a message to the chat display
    function addMessage(text, sender, type = 'text') { // type can be 'text' or 'html'
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'user' ? 'user-message' : 'system-message');
        if (type === 'html') {
            messageElement.innerHTML = text;
        } else {
            messageElement.textContent = text;
        }
        messageDisplay.appendChild(messageElement);
        messageDisplay.scrollTop = messageDisplay.scrollHeight; // Scroll to the bottom
    }

    // --- Event Listeners ---

    // Send button click
    sendButton.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (query) {
            addMessage(query, 'user');
            userInput.value = '';
            agentStatus.textContent = 'Agent: Processing...';

            try {
                const response = await fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: query }),
                });
                const data = await response.json();
                addMessage(data.response, 'system');
                
                // Update agent status
                if (data.agent_status) {
                    agentStatus.textContent = `Agent: ${data.agent_status}`;
                }
                
                // Update progress from backend
                if (data.progress !== undefined) {
                    updateProgress(data.progress);
                }
                
                // Update key facts from backend response
                if (data.key_facts && Array.isArray(data.key_facts)) {
                    updateKeyFacts(data.key_facts);
                }

            } catch (error) {
                console.error("Error sending message:", error);
                addMessage("Error: Could not connect to the server.", 'system');
                agentStatus.textContent = 'Agent: Error';
            }
        }
    });

    // Allow sending with Enter key
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });

    // Generate report button click
    generateReportButton.addEventListener('click', async () => {
        addMessage('System: Requesting report generation...', 'system');
        agentStatus.textContent = 'Agent: Synthesis Agent Activated';
        reportOutput.innerHTML = '<p>Generating report, please wait...</p>';

        try {
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
                // No body needed if the backend doesn't expect one for this specific request
            });
            const data = await response.json();

            if (data.status === 'success') {
                addMessage(`System: ${data.message}`, 'system');
                let reportContent = `<h3>${data.report_data.title}</h3><p>${data.report_data.summary}</p>`;
                
                // Handle key findings properly
                if (data.report_data.key_findings && data.report_data.key_findings.length > 0) {
                    reportContent += '<h4>Key Findings:</h4><ul>';
                    data.report_data.key_findings.forEach(finding => {
                        // Handle both string and object findings
                        if (typeof finding === 'string') {
                            reportContent += `<li>${finding}</li>`;
                        } else if (finding && finding.finding) {
                            reportContent += `<li>${finding.finding}</li>`;
                        }
                    });
                    reportContent += '</ul>';
                }
                
                if(data.report_data.download_link){
                    reportContent += `<p><a href="${data.report_data.download_link}" target="_blank" download>Download Full Report</a></p>`;
                }
                reportOutput.innerHTML = reportContent;
                updateProgress(100); // Report generation implies 100% progress for gathered info
            } else {
                addMessage(`System: Error generating report. ${data.message || ''}`, 'system');
                reportOutput.innerHTML = `<p>Could not generate report. ${data.message || ''}</p>`;
            }
            if (data.agent_status) {
                agentStatus.textContent = `Agent: ${data.agent_status}`;
            } else {
                 agentStatus.textContent = 'Agent: Idle';
            }

        } catch (error) {
            console.error("Error generating report:", error);
            addMessage("Error: Could not connect to the server to generate the report.", 'system');
            reportOutput.innerHTML = '<p>Error connecting to server.</p>';
            agentStatus.textContent = 'Agent: Error';
        }
    });

    // --- Helper Functions ---
    function updateProgress(percentage) {
        const clampedPercentage = Math.min(100, Math.max(0, percentage)); // Ensure percentage is between 0 and 100
        
        // Add a smooth transition effect
        progressBar.style.transition = 'width 0.5s ease-in-out';
        progressBar.style.width = clampedPercentage + '%';
        progressBar.textContent = clampedPercentage + '%';
        progressText.textContent = 'Information Completeness: ' + clampedPercentage + '%';
        
        // Add visual feedback for progress changes
        if (clampedPercentage > 0) {
            progressBar.style.backgroundColor = clampedPercentage >= 80 ? '#28a745' : 
                                               clampedPercentage >= 50 ? '#ffc107' : '#17a2b8';
        }
        
        // Log progress for debugging
        console.log(`Progress updated to: ${clampedPercentage}%`);
        
        if (clampedPercentage >= 100) {
             // addMessage('System: Information gathering complete. Ready to generate report.', 'system');
        }
    }

    function addKeyFact(fact) {
        // Prevent duplicate key facts
        const existingFacts = Array.from(keyFactsList.querySelectorAll('li')).map(li => li.textContent);
        if (!existingFacts.includes(fact)) {
            const listItem = document.createElement('li');
            listItem.textContent = fact;
            keyFactsList.appendChild(listItem);
        }
    }

    function updateKeyFacts(keyFactsArray) {
        // Clear existing facts to avoid duplicates and show current state
        keyFactsList.innerHTML = '';
        
        // Add all key facts from the backend
        keyFactsArray.forEach(fact => {
            const listItem = document.createElement('li');
            listItem.textContent = fact;
            keyFactsList.appendChild(listItem);
        });
        
        // If no facts provided, show a default message
        if (keyFactsArray.length === 0) {
            const listItem = document.createElement('li');
            listItem.textContent = '🔍 Investigation in progress...';
            listItem.style.fontStyle = 'italic';
            listItem.style.color = '#666';
            keyFactsList.appendChild(listItem);
        }
    }

    // Initial setup message
    addMessage('System: Welcome! Enter your intelligence query to begin.', 'system');
    updateProgress(0); // Initial progress

});

// Add some more specific styling for messages for better visual distinction
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
    .message {
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 15px;
        max-width: 70%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #dcf8c6;
        align-self: flex-end;
        margin-left: auto; /* Aligns to the right */
    }
    .system-message {
        background-color: #f1f0f0;
        align-self: flex-start;
        margin-right: auto; /* Aligns to the left */
    }
    .message-display {
        display: flex;
        flex-direction: column;
    }
`;
document.head.appendChild(styleSheet); 