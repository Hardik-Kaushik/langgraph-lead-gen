from .base_agent import BaseAgent
from typing import Dict, Any
import requests
import os

class DataEnrichmentAgent(BaseAgent):
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich lead data with additional information"""
        self.logger.info("Starting data enrichment...")
        
        leads = inputs.get("leads", [])
        enriched_leads = []
        
        for lead in leads:
            enriched_lead = self._enrich_lead(lead)
            enriched_leads.append(enriched_lead)
        
        output = {"enriched_leads": enriched_leads}
        self.log_execution(inputs, output)
        
        return output
    
    def _enrich_lead(self, lead: Dict) -> Dict:
        """Enrich a single lead using Clearbit"""
        email = lead.get("email", "")
        
        if not email:
            return {**lead, "role": "Unknown", "technologies": []}
        
        api_key = os.getenv("CLEARBIT_KEY")
        
        if not api_key:
            self.logger.warning("Clearbit API key not found")
            return {**lead, "role": lead.get("title", "Unknown"), "technologies": []}
        
        try:
            url = f"https://person-stream.clearbit.com/v2/combined/find?email={email}"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                person = data.get("person", {})
                company = data.get("company", {})
                
                return {
                    "company": lead.get("company", company.get("name", "")),
                    "contact": lead.get("contact_name", person.get("name", "")),
                    "email": email,
                    "role": person.get("employment", {}).get("title", "Unknown"),
                    "technologies": company.get("tech", [])[:5],  # Top 5 techs
                    "linkedin": lead.get("linkedin", "")
                }
            else:
                return {**lead, "role": "Unknown", "technologies": []}
                
        except Exception as e:
            self.logger.error(f"Enrichment error for {email}: {str(e)}")
            return {**lead, "role": "Unknown", "technologies": []}