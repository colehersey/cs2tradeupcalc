import math
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class WearTier(Enum):
    """CS2 skin wear tiers with their float ranges"""
    FACTORY_NEW = ("Factory New", 0.00, 0.07)
    MINIMAL_WEAR = ("Minimal Wear", 0.07, 0.15)
    FIELD_TESTED = ("Field-Tested", 0.15, 0.38)
    WELL_WORN = ("Well-Worn", 0.38, 0.45)
    BATTLE_SCARRED = ("Battle-Scarred", 0.45, 1.00)
    
    def __init__(self, display_name: str, min_float: float, max_float: float):
        self.display_name = display_name
        self.min_float = min_float
        self.max_float = max_float
    
    @classmethod
    def from_float(cls, float_value: float) -> 'WearTier':
        """Determine wear tier from float value"""
        for tier in cls:
            if tier.min_float <= float_value < tier.max_float:
                return tier
        return cls.BATTLE_SCARRED  # Fallback for edge cases


@dataclass
class ProbabilityDistribution:
    """Represents probability distribution for tradeup outcomes"""
    outcome_probabilities: Dict[str, float]  # skin_name -> probability
    float_distribution: Dict[WearTier, float]  # wear_tier -> probability
    expected_float: float
    float_variance: float


class ProbabilityCalculator:
    """Advanced probability calculations for CS2 tradeup contracts"""
    
    def calculate_outcome_probabilities(self, input_skins: List[Dict], 
                                      outcome_collection: List[Dict]) -> ProbabilityDistribution:
        """
        Calculate detailed probability distribution for tradeup outcomes
        
        Args:
            input_skins: List of input skin data dicts
            outcome_collection: List of possible outcome skin data dicts
            
        Returns:
            ProbabilityDistribution with all probability calculations
        """
        # Basic equal probability for each outcome
        num_outcomes = len(outcome_collection)
        if num_outcomes == 0:
            return ProbabilityDistribution({}, {}, 0.0, 0.0)
        
        base_probability = 1.0 / num_outcomes
        outcome_probabilities = {
            skin['market_hash_name']: base_probability 
            for skin in outcome_collection
        }
        
        # Calculate float distribution
        float_dist = self._calculate_float_distribution(input_skins, outcome_collection)
        
        # Calculate expected float and variance
        expected_float, float_variance = self._calculate_float_statistics(input_skins)
        
        return ProbabilityDistribution(
            outcome_probabilities=outcome_probabilities,
            float_distribution=float_dist,
            expected_float=expected_float,
            float_variance=float_variance
        )
    
    def _calculate_float_distribution(self, input_skins: List[Dict], 
                                    outcome_collection: List[Dict]) -> Dict[WearTier, float]:
        """
        Calculate probability distribution across wear tiers for output
        """
        # Calculate expected output float range
        input_floats = [skin['float_value'] for skin in input_skins]
        avg_float = statistics.mean(input_floats)
        float_std = statistics.stdev(input_floats) if len(input_floats) > 1 else 0.0
        
        # Output float is approximately average of inputs with some variance
        # CS2 uses a specific formula, but we'll approximate
        output_float_min = max(0.0, avg_float - float_std)
        output_float_max = min(1.0, avg_float + float_std)
        
        # Calculate probability for each wear tier
        wear_probabilities = {}
        for tier in WearTier:
            # Calculate overlap between output range and tier range
            overlap_min = max(output_float_min, tier.min_float)
            overlap_max = min(output_float_max, tier.max_float)
            
            if overlap_max > overlap_min:
                # Calculate probability as proportion of overlap
                tier_range = tier.max_float - tier.min_float
                overlap_range = overlap_max - overlap_min
                output_range = output_float_max - output_float_min
                
                if output_range > 0:
                    probability = overlap_range / output_range
                else:
                    probability = 1.0 if tier == WearTier.from_float(avg_float) else 0.0
            else:
                probability = 0.0
            
            wear_probabilities[tier] = probability
        
        # Normalize probabilities
        total_prob = sum(wear_probabilities.values())
        if total_prob > 0:
            wear_probabilities = {
                tier: prob / total_prob 
                for tier, prob in wear_probabilities.items()
            }
        
        return wear_probabilities
    
    def _calculate_float_statistics(self, input_skins: List[Dict]) -> Tuple[float, float]:
        """Calculate expected float and variance for output skin"""
        input_floats = [skin['float_value'] for skin in input_skins]
        
        if not input_floats:
            return 0.0, 0.0
        
        expected_float = statistics.mean(input_floats)
        float_variance = statistics.variance(input_floats) if len(input_floats) > 1 else 0.0
        
        return expected_float, float_variance
    
    def calculate_rarity_upgrade_probability(self, input_rarity: str) -> str:
        """
        Determine output rarity for tradeup contract
        
        CS2 tradeup contracts always upgrade to next rarity tier
        """
        rarity_hierarchy = [
            "Consumer Grade",
            "Industrial Grade", 
            "Mil-Spec Grade",
            "Restricted",
            "Classified",
            "Covert"
        ]
        
        try:
            current_index = rarity_hierarchy.index(input_rarity)
            if current_index < len(rarity_hierarchy) - 1:
                return rarity_hierarchy[current_index + 1]
            else:
                raise ValueError(f"Cannot upgrade beyond {input_rarity}")
        except ValueError:
            raise ValueError(f"Unknown rarity: {input_rarity}")
    
    def calculate_expected_value_with_uncertainty(self, outcome_probabilities: Dict[str, float],
                                                outcome_prices: Dict[str, int],
                                                input_cost: int,
                                                confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate expected value with confidence intervals
        
        Args:
            outcome_probabilities: skin_name -> probability
            outcome_prices: skin_name -> price in cents
            input_cost: total input cost in cents
            confidence_level: confidence level for intervals (e.g., 0.95 for 95%)
            
        Returns:
            Dict with expected_value, lower_bound, upper_bound, profit_probability
        """
        # Calculate expected value
        expected_output_value = sum(
            prob * outcome_prices.get(skin, 0)
            for skin, prob in outcome_probabilities.items()
        )
        expected_profit = expected_output_value - input_cost
        
        # Calculate variance
        expected_value_squared = sum(
            prob * (outcome_prices.get(skin, 0) ** 2)
            for skin, prob in outcome_probabilities.items()
        )
        variance = expected_value_squared - (expected_output_value ** 2)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        
        # Calculate confidence intervals (assuming normal distribution)
        z_score = 1.96 if confidence_level == 0.95 else 2.576  # 95% or 99%
        margin_of_error = z_score * std_dev
        
        lower_bound = expected_profit - margin_of_error
        upper_bound = expected_profit + margin_of_error
        
        # Calculate probability of profit
        profit_probability = self._calculate_profit_probability(
            outcome_probabilities, outcome_prices, input_cost
        )
        
        return {
            'expected_value': expected_profit,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'profit_probability': profit_probability,
            'standard_deviation': std_dev
        }
    
    def _calculate_profit_probability(self, outcome_probabilities: Dict[str, float],
                                    outcome_prices: Dict[str, int],
                                    input_cost: int) -> float:
        """Calculate probability that tradeup will be profitable"""
        profitable_probability = 0.0
        
        for skin, probability in outcome_probabilities.items():
            price = outcome_prices.get(skin, 0)
            if price > input_cost:
                profitable_probability += probability
        
        return profitable_probability
    
    def calculate_risk_metrics(self, outcome_probabilities: Dict[str, float],
                             outcome_prices: Dict[str, int],
                             input_cost: int) -> Dict[str, float]:
        """
        Calculate various risk metrics for the tradeup
        
        Returns:
            Dict with risk metrics including max_loss, sharpe_ratio, etc.
        """
        prices = [outcome_prices.get(skin, 0) for skin in outcome_probabilities.keys()]
        probabilities = list(outcome_probabilities.values())
        
        # Maximum possible loss
        min_outcome_value = min(prices) if prices else 0
        max_loss = input_cost - min_outcome_value
        
        # Maximum possible gain  
        max_outcome_value = max(prices) if prices else 0
        max_gain = max_outcome_value - input_cost
        
        # Calculate expected return
        expected_output = sum(p * price for p, price in zip(probabilities, prices))
        expected_return = (expected_output - input_cost) / input_cost if input_cost > 0 else 0
        
        # Calculate risk (standard deviation of returns)
        variance = sum(
            prob * ((price - input_cost) / input_cost - expected_return) ** 2
            for prob, price in zip(probabilities, prices)
        ) if input_cost > 0 else 0
        
        risk = math.sqrt(variance)
        
        # Sharpe ratio (return per unit of risk)
        sharpe_ratio = expected_return / risk if risk > 0 else float('inf')
        
        return {
            'max_loss': max_loss,
            'max_gain': max_gain,
            'expected_return_percent': expected_return * 100,
            'risk_percent': risk * 100,
            'sharpe_ratio': sharpe_ratio,
            'loss_probability': 1.0 - self._calculate_profit_probability(
                outcome_probabilities, outcome_prices, input_cost
            )
        }