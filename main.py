#!/usr/bin/env python3
"""
Main entry point for LangGraph Lead Generation Workflow
"""

import sys
from dotenv import load_dotenv
from langgraph_builder import LangGraphBuilder
from utils.logger import setup_logger
import json

def main():
    """Run the workflow"""
    
    # Load environment variables
    load_dotenv()
    
    # Setup logger
    logger = setup_logger("Main")
    
    logger.info("="*60)
    logger.info("LangGraph Autonomous Lead Generation Workflow")
    logger.info("="*60)
    
    try:
        # Create builder
        builder = LangGraphBuilder(config_path="config/workflow.json")
        
        # Build and execute workflow
        result = builder.execute()
        
        # Print results
        logger.info("\n" + "="*60)
        logger.info("WORKFLOW RESULTS")
        logger.info("="*60)
        
        for step_id, output in result["outputs"].items():
            logger.info(f"\n[{step_id}]")
            logger.info(json.dumps(output, indent=2))
        
        if result["errors"]:
            logger.error("\n" + "="*60)
            logger.error("ERRORS:")
            for error in result["errors"]:
                logger.error(f"  - {error}")
        
        logger.info("\n" + "="*60)
        logger.info("Workflow completed successfully!")
        logger.info("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())