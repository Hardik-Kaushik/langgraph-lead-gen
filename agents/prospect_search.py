from .base_agent import BaseAgent
from typing import Dict, Any
import requests
import os

class ProspectSearchAgent(BaseAgent):
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Search for prospects using Apollo and Clay APIs"""
        self.logger.info("Starting prospect search...")
        
        icp = inputs.get("icp", {})
        signals = inputs.get("signals", [])
        
        leads = []
        
        # Apollo API call
        apollo_leads = self._search_apollo(icp)
        leads.extend(apollo_leads)
        
        # Clay API call (if available)
        clay_leads = self._search_clay(icp, signals)
        leads.extend(clay_leads)
        
        output = {"leads": leads}
        self.log_execution(inputs, output)
        
        return output
    
    def _search_apollo(self, icp: Dict) -> list:
        """Search Apollo API for prospects"""
        api_key = os.getenv("APOLLO_API_KEY")
        
        if not api_key:
            self.logger.warning("Apollo API key not found")
            return self._generate_mock_leads()
        
        url = "https://api.apollo.io/v1/mixed_people/search"
        
        # Fixed headers format for Apollo API
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": api_key  # Apollo uses X-Api-Key header
        }
        
        # Build payload with safety checks
        payload = {
            "page": 1,
            "per_page": 10,
            "person_titles": ["VP of Sales", "Director of Sales", "Head of Business Development"]
        }
        
        # Add employee range if available
        if "employee_count" in icp:
            min_emp = icp["employee_count"].get("min", 100)
            max_emp = icp["employee_count"].get("max", 1000)
            payload["organization_num_employees_ranges"] = [f"{min_emp},{max_emp}"]
        
        try:
            self.logger.info(f"Calling Apollo API with payload: {payload}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Log the response for debugging
            self.logger.info(f"Apollo API response status: {response.status_code}")
            
            if response.status_code == 403:
                self.logger.error("Apollo API returned 403 Forbidden - Check your API key")
                self.logger.error("Get your API key from: https://app.apollo.io/#/settings/integrations/api")
                return self._generate_mock_leads()
            
            response.raise_for_status()
            
            data = response.json()
            people = data.get("people", [])
            
            leads = []
            for person in people:
                lead = {
                    "company": person.get("organization", {}).get("name", ""),
                    "contact_name": person.get("name", ""),
                    "email": person.get("email", ""),
                    "linkedin": person.get("linkedin_url", ""),
                    "signal": "apollo_match"
                }
                leads.append(lead)
            
            self.logger.info(f"Found {len(leads)} leads from Apollo")
            return leads if leads else self._generate_mock_leads()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Apollo API error: {str(e)}")
            return self._generate_mock_leads()
    
    def _search_clay(self, icp: Dict, signals: list) -> list:
        """Search Clay API for prospects"""
        # Placeholder - Clay API integration
        self.logger.info("Clay API search (placeholder - using mock data)")
        return []
    
    def _generate_mock_leads(self) -> list:
        """Generate mock leads for testing when API is unavailable"""
        self.logger.info("Generating mock leads for demonstration")
        
        mock_leads = [
            {
                "company": "TechCorp Inc",
                "contact_name": "John Smith",
                "email": "john.smith@techcorp.com",
                "linkedin": "linkedin.com/in/johnsmith",
                "signal": "mock_data"
            },
            {
                "company": "SaaS Solutions Ltd",
                "contact_name": "Sarah Johnson",
                "email": "sarah.j@saassolutions.com",
                "linkedin": "linkedin.com/in/sarahjohnson",
                "signal": "mock_data"
            },
            {
                "company": "Data Analytics Pro",
                "contact_name": "Michael Chen",
                "email": "m.chen@dataanalytics.com",
                "linkedin": "linkedin.com/in/michaelchen",
                "signal": "mock_data"
            },
            {
                "company": "Cloud Services Group",
                "contact_name": "Emily Davis",
                "email": "emily.davis@cloudservices.com",
                "linkedin": "linkedin.com/in/emilydavis",
                "signal": "mock_data"
            },
            {
                "company": "AI Innovations Inc",
                "contact_name": "Robert Martinez",
                "email": "r.martinez@aiinnovations.com",
                "linkedin": "linkedin.com/in/robertmartinez",
                "signal": "mock_data"
            }
        ]
        
        return mock_leads