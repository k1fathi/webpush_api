import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from models.schemas.ab_test import AbTest, WinningCriteria
from models.schemas.test_variant import TestVariant
from repositories.ab_test import AbTestRepository
from repositories.test_variant import TestVariantRepository
from repositories.template import TemplateRepository
from repositories.analytics import AnalyticsRepository
from repositories.campaign import CampaignRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class AbTestService:
    def __init__(self):
        self.ab_test_repo = AbTestRepository()
        self.test_variant_repo = TestVariantRepository()
        self.template_repo = TemplateRepository()
        self.analytics_repo = AnalyticsRepository()
        self.campaign_repo = CampaignRepository()
    
    async def create_test(self, campaign_id: str, test_data: Dict) -> AbTest:
        """Create a new A/B test for a campaign"""
        # First check if campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Create the A/B test
        test_data["campaign_id"] = campaign_id
        ab_test = AbTest(**test_data)
        created_test = await self.ab_test_repo.create(ab_test)
        
        audit_log(f"Created A/B test '{created_test.name}' for campaign {campaign_id}")
        return created_test
    
    async def add_variant(self, ab_test_id: str, variant_data: Dict) -> TestVariant:
        """Add a test variant to an A/B test"""
        # Check if the A/B test exists
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
        
        # Check if template exists
        template = await self.template_repo.get(variant_data["template_id"])
        if not template:
            raise ValueError(f"Template with ID {variant_data['template_id']} not found")
            
        # Create the variant
        variant_data["ab_test_id"] = ab_test_id
        variant = TestVariant(**variant_data)
        created_variant = await self.test_variant_repo.create(variant)
        
        # Update the variant count on the A/B test
        variants_count = await self.test_variant_repo.count_by_test(ab_test_id)
        if variants_count != ab_test.variant_count:
            ab_test.variant_count = variants_count
            await self.ab_test_repo.update(ab_test_id, ab_test)
        
        audit_log(f"Added variant '{created_variant.name}' to A/B test {ab_test_id}")
        return created_variant
    
    async def get_test(self, ab_test_id: str) -> Optional[AbTest]:
        """Get an A/B test by ID"""
        return await self.ab_test_repo.get(ab_test_id)
    
    async def get_variants(self, ab_test_id: str) -> List[TestVariant]:
        """Get all variants for an A/B test"""
        return await self.test_variant_repo.get_by_test(ab_test_id)
    
    async def update_test(self, ab_test_id: str, test_data: Dict) -> AbTest:
        """Update an A/B test"""
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
            
        # Update the test
        for key, value in test_data.items():
            setattr(ab_test, key, value)
            
        updated_test = await self.ab_test_repo.update(ab_test_id, ab_test)
        audit_log(f"Updated A/B test {ab_test_id}")
        return updated_test
    
    async def activate_test(self, ab_test_id: str) -> AbTest:
        """Activate an A/B test"""
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
        
        # Check if test has at least two variants
        variants = await self.test_variant_repo.get_by_test(ab_test_id)
        if len(variants) < 2:
            raise ValueError("A/B test must have at least two variants before activation")
        
        # Set the start date to now if not already set
        if not ab_test.start_date:
            ab_test.start_date = datetime.now()
            
        updated_test = await self.ab_test_repo.update(ab_test_id, ab_test)
        audit_log(f"Activated A/B test {ab_test_id}")
        return updated_test
    
    async def complete_test(self, ab_test_id: str) -> AbTest:
        """Mark an A/B test as complete"""
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
        
        # Set the end date to now
        ab_test.end_date = datetime.now()
        updated_test = await self.ab_test_repo.update(ab_test_id, ab_test)
        
        audit_log(f"Completed A/B test {ab_test_id}")
        return updated_test
    
    async def analyze_results(self, ab_test_id: str) -> Dict:
        """Analyze the results of an A/B test"""
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
        
        variants = await self.test_variant_repo.get_by_test(ab_test_id)
        if not variants:
            raise ValueError(f"No variants found for A/B test {ab_test_id}")
        
        results = {}
        for variant in variants:
            # Calculate performance metrics for each variant
            results[variant.id] = {
                "name": variant.name,
                "sent_count": variant.sent_count,
                "opened_count": variant.opened_count,
                "clicked_count": variant.clicked_count,
                "open_rate": variant.opened_count / variant.sent_count if variant.sent_count > 0 else 0,
                "click_rate": variant.clicked_count / variant.sent_count if variant.sent_count > 0 else 0,
                "click_to_open_rate": variant.clicked_count / variant.opened_count if variant.opened_count > 0 else 0,
            }
        
        # Determine the winning variant based on the criteria
        winner = await self._determine_winner(ab_test, variants)
        results["winner"] = winner[0].id if winner else None
        results["is_significant"] = winner[1] if winner else False
        
        return results
    
    async def _determine_winner(self, ab_test: AbTest, variants: List[TestVariant]) -> Tuple[Optional[TestVariant], bool]:
        """
        Determine the winning variant based on the test's winning criteria.
        Returns a tuple of (winning_variant, is_statistically_significant)
        """
        if not variants or len(variants) < 2:
            return None, False
            
        # Sort variants based on the winning criteria
        if ab_test.winning_criteria == WinningCriteria.OPEN_RATE:
            variants.sort(key=lambda v: v.opened_count / v.sent_count if v.sent_count > 0 else 0, reverse=True)
        elif ab_test.winning_criteria == WinningCriteria.CLICK_RATE:
            variants.sort(key=lambda v: v.clicked_count / v.sent_count if v.sent_count > 0 else 0, reverse=True)
        elif ab_test.winning_criteria == WinningCriteria.CONVERSION:
            # For conversion, we'd need to fetch conversion data from analytics
            # This is a simplified placeholder implementation
            conversion_rates = {}
            for variant in variants:
                conversions = await self.analytics_repo.get_conversions_for_variant(variant.id)
                conversion_rates[variant.id] = len(conversions) / variant.sent_count if variant.sent_count > 0 else 0
            variants.sort(key=lambda v: conversion_rates.get(v.id, 0), reverse=True)
        else:  # Default to engagement (combination of open and click)
            variants.sort(
                key=lambda v: (v.opened_count + v.clicked_count * 2) / v.sent_count if v.sent_count > 0 else 0,
                reverse=True
            )
        
        # Simple statistical significance check (chi-square or z-test would be more appropriate)
        # This is just a placeholder - in a real implementation you'd use a proper statistical test
        best_variant = variants[0]
        runner_up = variants[1]
        
        # Calculate improvement percentage
        if ab_test.winning_criteria == WinningCriteria.OPEN_RATE:
            best_rate = best_variant.opened_count / best_variant.sent_count if best_variant.sent_count > 0 else 0
            runner_rate = runner_up.opened_count / runner_up.sent_count if runner_up.sent_count > 0 else 0
        elif ab_test.winning_criteria == WinningCriteria.CLICK_RATE:
            best_rate = best_variant.clicked_count / best_variant.sent_count if best_variant.sent_count > 0 else 0
            runner_rate = runner_up.clicked_count / runner_up.sent_count if runner_up.sent_count > 0 else 0
        else:
            # Default to a combined metric for other criteria
            best_rate = (best_variant.opened_count + best_variant.clicked_count) / best_variant.sent_count if best_variant.sent_count > 0 else 0
            runner_rate = (runner_up.opened_count + runner_up.clicked_count) / runner_up.sent_count if runner_up.sent_count > 0 else 0
        
        # Simple significance check - if improvement is > 10% and samples are large enough
        improvement = (best_rate - runner_rate) / runner_rate if runner_rate > 0 else 0
        is_significant = improvement > 0.1 and best_variant.sent_count > 100 and runner_up.sent_count > 100
        
        return best_variant, is_significant
    
    async def apply_winning_variant(self, ab_test_id: str) -> bool:
        """Apply the winning variant to the campaign"""
        ab_test = await self.ab_test_repo.get(ab_test_id)
        if not ab_test:
            raise ValueError(f"A/B test with ID {ab_test_id} not found")
        
        # Analyze results to find the winner
        results = await self.analyze_results(ab_test_id)
        winner_id = results.get("winner")
        
        if not winner_id or not results.get("is_significant", False):
            logger.warning(f"No significant winner found for A/B test {ab_test_id}")
            return False
            
        # Get the winning variant
        winner = await self.test_variant_repo.get(winner_id)
        if not winner:
            logger.error(f"Winner variant {winner_id} not found")
            return False
            
        # Update the campaign to use the winning template
        campaign = await self.campaign_repo.get(ab_test.campaign_id)
        if not campaign:
            logger.error(f"Campaign {ab_test.campaign_id} not found")
            return False
            
        # Update the campaign with the winning template
        campaign.template_id = winner.template_id
        await self.campaign_repo.update(campaign.id, campaign)
        
        audit_log(f"Applied winning variant {winner.name} to campaign {campaign.id}")
        return True
