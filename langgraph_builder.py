import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from utils.logger import setup_logger

# Import all agents
from agents import (
    ProspectSearchAgent,
    DataEnrichmentAgent,
    ScoringAgent,
    OutreachContentAgent,
    OutreachExecutorAgent,
    ResponseTrackerAgent,
    FeedbackTrainerAgent
)

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

class WorkflowState(TypedDict):
    """State passed between nodes in the graph"""
    current_step: str
    data: Dict[str, Any]
    outputs: Dict[str, Any]
    errors: List[str]

class LangGraphBuilder:
    """Builds and executes LangGraph workflow from JSON config"""
    
    def __init__(self, config_path: str = "config/workflow.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.agent_map = self._create_agent_map()
        self.graph = None
        
    def _load_config(self) -> Dict:
        """Load workflow configuration from JSON"""
        logger.info(f"Loading workflow config from {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Replace environment variable placeholders
        config_str = json.dumps(config)
        for key, value in os.environ.items():
            config_str = config_str.replace(f"{{{{{key}}}}}", value)
        
        return json.loads(config_str)
    
    def _create_agent_map(self) -> Dict:
        """Map agent names to classes"""
        return {
            "ProspectSearchAgent": ProspectSearchAgent,
            "DataEnrichmentAgent": DataEnrichmentAgent,
            "ScoringAgent": ScoringAgent,
            "OutreachContentAgent": OutreachContentAgent,
            "OutreachExecutorAgent": OutreachExecutorAgent,
            "ResponseTrackerAgent": ResponseTrackerAgent,
            "FeedbackTrainerAgent": FeedbackTrainerAgent
        }
    
    def build_graph(self) -> StateGraph:
        """Build LangGraph from config"""
        logger.info("Building LangGraph workflow...")
        
        # Create graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        steps = self.config.get("steps", [])
        
        for step in steps:
            step_id = step["id"]
            agent_class_name = step["agent"]
            
            # Create agent instance
            agent_class = self.agent_map.get(agent_class_name)
            if not agent_class:
                raise ValueError(f"Unknown agent: {agent_class_name}")
            
            agent = agent_class(
                agent_id=step_id,
                instructions=step.get("instructions", ""),
                tools=step.get("tools", [])
            )
            
            # Create node function
            def create_node_fn(agent_instance, step_config):
                def node_fn(state: WorkflowState) -> WorkflowState:
                    logger.info(f"Executing node: {step_config['id']}")
                    
                    try:
                        # Resolve inputs from previous outputs
                        inputs = self._resolve_inputs(
                            step_config.get("inputs", {}),
                            state["outputs"]
                        )
                        
                        # Execute agent
                        output = agent_instance.execute(inputs)
                        
                        # Update state
                        state["outputs"][step_config["id"]] = output
                        state["current_step"] = step_config["id"]
                        
                    except Exception as e:
                        logger.error(f"Error in node {step_config['id']}: {str(e)}")
                        state["errors"].append(f"{step_config['id']}: {str(e)}")
                    
                    return state
                
                return node_fn
            
            # Add node to graph
            workflow.add_node(step_id, create_node_fn(agent, step))
        
        # Add edges (sequential flow)
        for i in range(len(steps) - 1):
            workflow.add_edge(steps[i]["id"], steps[i + 1]["id"])
        
        # Set entry point and end
        workflow.set_entry_point(steps[0]["id"])
        workflow.add_edge(steps[-1]["id"], END)
        
        self.graph = workflow.compile()
        logger.info("LangGraph workflow built successfully")
        
        return self.graph
    
    def _resolve_inputs(self, input_config: Dict, outputs: Dict) -> Dict:
        """Resolve input references from previous step outputs"""
        resolved = {}
        
        for key, value in input_config.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Parse reference like {{step_id.output.field}}
                ref = value[2:-2].strip()
                parts = ref.split(".")
                
                if parts[0] == "config":
                    # Reference to config
                    config_value = self.config.get("config", {})
                    for part in parts[1:]:
                        config_value = config_value.get(part, {})
                    resolved[key] = config_value
                else:
                    # Reference to previous step output
                    step_id = parts[0]
                    if step_id in outputs:
                        result = outputs[step_id]
                        for part in parts[1:]:
                            if part == "output":
                                continue
                            result = result.get(part, {})
                        resolved[key] = result
                    else:
                        resolved[key] = None
            else:
                resolved[key] = value
        
        return resolved
    
    def execute(self) -> Dict[str, Any]:
        """Execute the workflow"""
        if not self.graph:
            self.build_graph()
        
        logger.info("Starting workflow execution...")
        
        # Initial state
        initial_state = WorkflowState(
            current_step="",
            data={},
            outputs={},
            errors=[]
        )
        
        # Execute graph
        final_state = self.graph.invoke(initial_state)
        
        logger.info("Workflow execution completed")
        
        if final_state["errors"]:
            logger.warning(f"Workflow completed with {len(final_state['errors'])} errors")
        
        return final_state