from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents in the workflow"""
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict]):
        self.agent_id = agent_id
        self.instructions = instructions
        self.tools = tools
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic"""
        pass
    
    def log_execution(self, inputs: Dict, outputs: Dict):
        """Log agent execution details"""
        self.logger.info(f"Agent {self.agent_id} executed at {datetime.now()}")
        self.logger.debug(f"Inputs: {inputs}")
        self.logger.debug(f"Outputs: {outputs}")
        
    def validate_output(self, output: Dict, schema: Dict) -> bool:
        """Validate output against expected schema"""
        # Simple validation - can be enhanced
        for key in schema.keys():
            if key not in output:
                self.logger.warning(f"Missing key in output: {key}")
                return False
        return True