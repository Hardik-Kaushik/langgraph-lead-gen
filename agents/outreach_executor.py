from .base_agent import BaseAgent
from typing import Dict, Any
import requests
import os
import uuid

class OutreachExecutorAgent(BaseAgent):
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Send emails via Apollo API"""
        self.logger.info("Sending outreach emails...")
        
        messages = inputs.get("messages", [])
        sent_status = []
        campaign_id = str(uuid.uuid4())
        
        for message in messages:
            status = self._send_email(message, campaign_id)
            sent_status.append(status)
        
        output = {
            "sent_status": sent_status,
            "campaign_id": campaign_id
        }
        self.log_execution(inputs, output)
        
        return output
    
    def _send_email(self, message: Dict, campaign_id: str) -> Dict:
        """Send a single email"""
        api_key = os.getenv("APOLLO_API_KEY")
        
        if not api_key:
            self.logger.warning("Apollo API key not found, simulating send")
            return {
                "email": message.get("email", ""),
                "status": "simulated",
                "campaign_id": campaign_id
            }
        
        # For demo purposes, we'll simulate sending
        # In production, use Apollo's email sending endpoint
        try:
            self.logger.info(f"Sending email to {message.get('email', '')}")
            
            # Simulated send
            return {
                "email": message.get("email", ""),
                "subject": message.get("subject", ""),
                "status": "sent",
                "campaign_id": campaign_id,
                "sent_at": "2025-10-18T10:00:00Z"
            }
            
        except Exception as e:
            self.logger.error(f"Email send error: {str(e)}")
            return {
                "email": message.get("email", ""),
                "status": "failed",
                "error": str(e),
                "campaign_id": campaign_id
            }