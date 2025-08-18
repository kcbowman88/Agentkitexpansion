#!/usr/bin/env python3
"""
Test script for the KB implementation.
"""

import os
import sys
import logging
from kb_processor import KBProcessor

def test_kb_processor():
    """
    Test the KB processor functionality.
    """
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialize KB processor
        print("Initializing KB processor...")
        # Get OpenAI API key from environment variable
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        kb_processor = KBProcessor(openai_api_key=openai_api_key)
        
        # Test queries
        test_queries = [
            "What are the benefits of this business model?",
            "How much money can I make with this program?",
            "What is the Rank and Bank strategy?",
            "How does the digital real estate model work?"
        ]
        
        print("\nTesting KB queries:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            response = kb_processor.query(query)
            print(f"   Response: {response}")
            
            # Print metrics after each query
            if kb_processor.metrics['query_count'] > 0:
                avg_time = kb_processor.metrics['total_query_time'] / kb_processor.metrics['query_count']
                print(f"   Average query time: {avg_time:.3f}s")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        logging.error(f"Error testing KB processor: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    test_kb_processor()