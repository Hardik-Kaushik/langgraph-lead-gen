import os
import requests
from typing import Dict, Any

class APIClient:
    """Base API client with common functionality"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
    
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

class ApolloClient(APIClient):
    """Apollo API client"""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.apollo.io/v1",
            api_key=os.getenv("APOLLO_API_KEY", "")
        )
    
    def search_people(self, criteria: Dict) -> list:
        """Search for people matching criteria"""
        return self.post("mixed_people/search", criteria)