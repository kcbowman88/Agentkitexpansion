"""
A/B Testing Framework for Conversation Nodes and Transitions
"""
import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class ABTestVariant:
    """Represents a variant in an A/B test"""
    id: str
    name: str
    weight: float  # Weight for random selection (0.0 to 1.0)
    node_id: str  # The node this variant represents

@dataclass
class ABTest:
    """Represents an A/B test for a conversation node"""
    id: str
    name: str
    variants: List[ABTestVariant]
    enabled: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ABTestManager:
    """Manages A/B tests for conversation nodes and transitions"""
    
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
        self.test_results: Dict[str, Dict[str, int]] = {}  # test_id -> {variant_id -> conversion_count}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {test_id -> variant_id}
        
    def add_test(self, test: ABTest):
        """
        Add a new A/B test
        
        Args:
            test (ABTest): The A/B test to add
        """
        self.tests[test.id] = test
        self.test_results[test.id] = {}
        logging.info(f"Added A/B test: {test.name} (ID: {test.id})")
        
    def assign_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """
        Assign a variant to a user for a specific test
        
        Args:
            test_id (str): The ID of the test
            user_id (str): The ID of the user
            
        Returns:
            Optional[str]: The assigned variant ID, or None if no test found
        """
        if test_id not in self.tests:
            return None
            
        test = self.tests[test_id]
        if not test.enabled:
            return None
            
        # Check if user already has an assignment
        if user_id in self.user_assignments and test_id in self.user_assignments[user_id]:
            return self.user_assignments[user_id][test_id]
            
        # Assign a new variant based on weights
        variant = self._weighted_random_choice(test.variants)
        if variant:
            # Record the assignment
            if user_id not in self.user_assignments:
                self.user_assignments[user_id] = {}
            self.user_assignments[user_id][test_id] = variant.id
            
            # Initialize result tracking for this variant if needed
            if variant.id not in self.test_results[test_id]:
                self.test_results[test_id][variant.id] = 0
                
            logging.info(f"Assigned user {user_id} to variant {variant.id} for test {test_id}")
            return variant.id
            
        return None
        
    def get_node_for_user(self, test_id: str, user_id: str) -> Optional[str]:
        """
        Get the node ID for a user based on their A/B test assignment
        
        Args:
            test_id (str): The ID of the test
            user_id (str): The ID of the user
            
        Returns:
            Optional[str]: The node ID for the assigned variant, or None if no assignment
        """
        variant_id = self.assign_variant(test_id, user_id)
        if not variant_id:
            return None
            
        test = self.tests[test_id]
        variant = next((v for v in test.variants if v.id == variant_id), None)
        if variant:
            return variant.node_id
            
        return None
        
    def record_conversion(self, test_id: str, variant_id: str):
        """
        Record a conversion for a specific variant in a test
        
        Args:
            test_id (str): The ID of the test
            variant_id (str): The ID of the variant
        """
        if test_id in self.test_results and variant_id in self.test_results[test_id]:
            self.test_results[test_id][variant_id] += 1
            logging.info(f"Recorded conversion for test {test_id}, variant {variant_id}")
            
    def get_test_results(self, test_id: str) -> Optional[Dict[str, int]]:
        """
        Get the results for a specific test
        
        Args:
            test_id (str): The ID of the test
            
        Returns:
            Optional[Dict[str, int]]: The results, or None if test not found
        """
        return self.test_results.get(test_id)
        
    def _weighted_random_choice(self, variants: List[ABTestVariant]) -> Optional[ABTestVariant]:
        """
        Select a variant based on weights
        
        Args:
            variants (List[ABTestVariant]): List of variants to choose from
            
        Returns:
            Optional[ABTestVariant]: The selected variant, or None if no variants
        """
        if not variants:
            return None
            
        total_weight = sum(v.weight for v in variants)
        if total_weight <= 0:
            # If all weights are zero, pick randomly
            return random.choice(variants)
            
        # Select based on weights
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for variant in variants:
            cumulative_weight += variant.weight
            if rand_val <= cumulative_weight:
                return variant
                
        # Fallback (shouldn't happen, but just in case)
        return variants[-1]

# Global instance
ab_test_manager = ABTestManager()

# Example usage:
# Create an A/B test for an introduction node
# intro_test = ABTest(
#     id="intro_test_001",
#     name="Introduction Node A/B Test",
#     variants=[
#         ABTestVariant(id="variant_a", name="Original Intro", weight=0.5, node_id="N_Opener_StackingIncomeHook_V3_CreativeTactic"),
#         ABTestVariant(id="variant_b", name="New Intro", weight=0.5, node_id="N_Opener_StackingIncomeHook_V3_CreativeTactic_VariantB")
#     ]
# )
# 
# ab_test_manager.add_test(intro_test)