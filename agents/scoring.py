from .base_agent import BaseAgent
from typing import Dict, Any

class ScoringAgent(BaseAgent):
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Score and rank leads based on ICP fit"""
        self.logger.info("Starting lead scoring...")
        
        enriched_leads = inputs.get("enriched_leads", [])
        scoring_criteria = inputs.get("scoring_criteria", {})
        
        scored_leads = []
        
        for lead in enriched_leads:
            score = self._calculate_score(lead, scoring_criteria)
            scored_lead = {**lead, "score": score}
            scored_leads.append(scored_lead)
        
        # Sort by score descending
        ranked_leads = sorted(scored_leads, key=lambda x: x.get("score", 0), reverse=True)
        
        output = {"ranked_leads": ranked_leads}
        self.log_execution(inputs, output)
        
        return output
    
    def _calculate_score(self, lead: Dict, criteria: Dict) -> float:
        """Calculate ICP fit score for a lead"""
        score = 0.0
        
        # Technology match score
        tech_weight = criteria.get("technology_weight", 0.3)
        technologies = lead.get("technologies", [])
        if technologies:
            score += tech_weight * min(len(technologies) / 5, 1.0)
        
        # Role relevance score
        role = lead.get("role", "").lower()
        relevant_roles = ["vp", "director", "head", "chief", "manager"]
        if any(r in role for r in relevant_roles):
            score += 0.3
        
        # Signal score
        signal_weight = criteria.get("signal_weight", 0.2)
        if lead.get("signal"):
            score += signal_weight
        
        # Random baseline for demo
        score += 0.2
        
        return round(min(score, 1.0), 2)