from .base_agent import BaseAgent
from typing import Dict, Any
import random

class ResponseTrackerAgent(BaseAgent):
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Track email responses and engagement"""
        self.logger.info("Tracking email responses...")
        
        campaign_id = inputs.get("campaign_id", "")
        
        # In production, query Apollo API for actual metrics
        # For demo, generate simulated response data
        responses = self._get_campaign_metrics(campaign_id)
        
        output = {"responses": responses}
        self.log_execution(inputs, output)
        
        return output
    
    def _get_campaign_metrics(self, campaign_id: str) -> list:
        """Get metrics for a campaign (simulated)"""
        
        # Simulate response data
        responses = []
        
        for i in range(5):
            response = {
                "email": f"lead{i}@example.com",
                "campaign_id": campaign_id,
                "opened": random.choice([True, False]),
                "clicked": random.choice([True, False, False]),
                "replied": random.choice([True, False, False, False]),
                "meeting_booked": random.choice([True, False, False, False, False])
            }
            responses.append(response)
        
        open_rate = sum(1 for r in responses if r["opened"]) / len(responses)
        reply_rate = sum(1 for r in responses if r["replied"]) / len(responses)
        
        self.logger.info(f"Campaign metrics - Open: {open_rate:.1%}, Reply: {reply_rate:.1%}")
        
        return responses