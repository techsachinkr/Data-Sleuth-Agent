from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime, timedelta
from models.schemas import Evidence, InformationQuality
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Advanced memory management with context window handling"""
    
    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        self.memory_store: Dict[str, List[Evidence]] = {}
        self.context_summaries: Dict[str, str] = {}
        self.access_log: Dict[str, datetime] = {}
    
    def store_evidence(self, session_id: str, evidence: Evidence) -> None:
        """Store evidence with automatic summarization when context limit reached"""
        if session_id not in self.memory_store:
            self.memory_store[session_id] = []
        
        self.memory_store[session_id].append(evidence)
        self.access_log[session_id] = datetime.now()
        
        # Check if we need to summarize
        if self._estimate_tokens(session_id) > self.max_tokens:
            self._summarize_context(session_id)
    
    def get_evidence(self, session_id: str, limit: Optional[int] = None) -> List[Evidence]:
        """Retrieve evidence for a session"""
        evidence_list = self.memory_store.get(session_id, [])
        if limit:
            return evidence_list[-limit:]
        return evidence_list
    
    def get_context_summary(self, session_id: str) -> Optional[str]:
        """Get context summary for a session"""
        return self.context_summaries.get(session_id)
    
    def _estimate_tokens(self, session_id: str) -> int:
        """Rough token estimation"""
        evidence_list = self.memory_store.get(session_id, [])
        total_content = ""
        for evidence in evidence_list:
            total_content += evidence.content
        return len(total_content.split()) * 1.3  # Rough approximation
    
    def _summarize_context(self, session_id: str) -> None:
        """Compress old context into summaries"""
        evidence_list = self.memory_store[session_id]
        
        if len(evidence_list) > 10:
            # Keep recent evidence, summarize older ones
            recent_evidence = evidence_list[-5:]
            older_evidence = evidence_list[:-5]
            
            # Create summary of older evidence
            summary = self._create_evidence_summary(older_evidence)
            self.context_summaries[session_id] = summary
            self.memory_store[session_id] = recent_evidence
            
            logger.info(f"Context summarized for session {session_id}")
    
    def _create_evidence_summary(self, evidence_list: List[Evidence]) -> str:
        """Create a concise summary of evidence"""
        high_quality_evidence = [
            e for e in evidence_list 
            if e.quality in [InformationQuality.HIGH, InformationQuality.MEDIUM]
        ]
        
        key_points = []
        for evidence in high_quality_evidence:
            key_points.append(f"- {evidence.content[:200]}...")
        
        return "\n".join(key_points)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """Clean up old session data"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, last_access in self.access_log.items():
            if last_access < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.memory_store.pop(session_id, None)
            self.context_summaries.pop(session_id, None)
            self.access_log.pop(session_id, None)
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")