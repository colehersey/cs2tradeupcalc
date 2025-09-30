from typing import List, Dict, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class SkinData:
    """Represents a CS2 skin with market data"""
    market_hash_name: str
    collection: str
    rarity: str
    float_value: float
    price_cents: int
    wear_name: str
    is_stattrak: bool = False
    is_souvenir: bool = False


@dataclass
class TradeupInput:
    """Represents the 10 input skins for a tradeup contract"""
    input_skins: List[SkinData]
    
    def __post_init__(self):
        if len(self.input_skins) != 10:
            raise ValueError("Tradeup contract requires exactly 10 input skins")


@dataclass
class TradeupOutcome:
    """Represents a possible outcome from a tradeup"""
    skin_data: SkinData
    probability: float
    expected_float_range: Tuple[float, float]


@dataclass
class ExpectedValueResult:
    """Results of expected value calculation"""
    total_input_cost_cents: int
    expected_output_value_cents: float
    expected_profit_cents: float
    profit_margin_percent: float
    possible_outcomes: List[TradeupOutcome]
    break_even_probability: float


class TradeupCalculator:
    """Core engine for calculating tradeup contract expected values"""
    
    def calculate_expected_value(self, tradeup_input: TradeupInput, 
                               outcome_collection_skins: List[SkinData]) -> ExpectedValueResult:
        """
        Calculate expected value for a tradeup contract
        
        Args:
            tradeup_input: The 10 input skins
            outcome_collection_skins: All possible outcome skins from target collection
            
        Returns:
            ExpectedValueResult with complete analysis
        """
        # Calculate total input cost
        total_input_cost = self._calculate_input_cost(tradeup_input.input_skins)
        
        # Calculate float range for outcomes
        input_float_range = self._calculate_output_float_range(tradeup_input.input_skins)
        
        # Determine possible outcomes and their probabilities
        possible_outcomes = self._calculate_outcome_probabilities(
            outcome_collection_skins, input_float_range
        )
        
        # Calculate expected output value
        expected_output_value = sum(
            outcome.skin_data.price_cents * outcome.probability 
            for outcome in possible_outcomes
        )
        
        # Calculate profit metrics
        expected_profit = expected_output_value - total_input_cost
        profit_margin = (expected_profit / total_input_cost) * 100 if total_input_cost > 0 else 0
        
        # Calculate break-even probability
        break_even_prob = self._calculate_break_even_probability(
            total_input_cost, possible_outcomes
        )
        
        return ExpectedValueResult(
            total_input_cost_cents=total_input_cost,
            expected_output_value_cents=expected_output_value,
            expected_profit_cents=expected_profit,
            profit_margin_percent=profit_margin,
            possible_outcomes=possible_outcomes,
            break_even_probability=break_even_prob
        )
    
    def _calculate_input_cost(self, input_skins: List[SkinData]) -> int:
        """Calculate total cost of purchasing input skins at market price"""
        return sum(skin.price_cents for skin in input_skins)
    
    def _calculate_output_float_range(self, input_skins: List[SkinData]) -> Tuple[float, float]:
        """
        Calculate the float range for output skin based on input skins
        Formula: output_float = average(input_floats) with some variation
        """
        input_floats = [skin.float_value for skin in input_skins]
        
        # CS2 tradeup float calculation:
        # Output float is average of input floats with small random variation
        min_input_float = min(input_floats)
        max_input_float = max(input_floats)
        avg_input_float = statistics.mean(input_floats)
        
        # Output range is typically average ± some variance
        # For simplicity, using min/max of inputs as bounds
        return (min_input_float, max_input_float)
    
    def _calculate_outcome_probabilities(self, outcome_skins: List[SkinData], 
                                       float_range: Tuple[float, float]) -> List[TradeupOutcome]:
        """
        Calculate probability and expected value for each possible outcome
        
        In CS2, each skin in the outcome collection has equal probability
        """
        if not outcome_skins:
            return []
        
        # Filter outcomes that could realistically be obtained given float range
        valid_outcomes = self._filter_outcomes_by_float_range(outcome_skins, float_range)
        
        if not valid_outcomes:
            return []
        
        # Equal probability for each outcome
        probability_per_outcome = 1.0 / len(valid_outcomes)
        
        outcomes = []
        for skin in valid_outcomes:
            outcome = TradeupOutcome(
                skin_data=skin,
                probability=probability_per_outcome,
                expected_float_range=float_range
            )
            outcomes.append(outcome)
        
        return outcomes
    
    def _filter_outcomes_by_float_range(self, outcome_skins: List[SkinData], 
                                      float_range: Tuple[float, float]) -> List[SkinData]:
        """
        Filter outcome skins that are possible given the input float range
        
        For now, include all skins. Future enhancement: filter by realistic float constraints
        """
        # TODO: Implement float-based filtering for wear tiers
        # For example, if input produces 0.15-0.25 float range, exclude Factory New outcomes
        return outcome_skins
    
    def _calculate_break_even_probability(self, input_cost: int, 
                                        outcomes: List[TradeupOutcome]) -> float:
        """
        Calculate what probability of profitable outcomes is needed to break even
        """
        if not outcomes:
            return 0.0
        
        # Find outcomes that are profitable (value > input cost)
        profitable_outcomes = [o for o in outcomes if o.skin_data.price_cents >= input_cost]
        
        if not profitable_outcomes:
            return 1.0  # Need 100% chance of profit (impossible)
        
        # Sum probability of profitable outcomes
        profitable_probability = sum(o.probability for o in profitable_outcomes)
        
        return profitable_probability
    
    def validate_tradeup_inputs(self, input_skins: List[SkinData]) -> List[str]:
        """
        Validate that input skins can form a valid tradeup contract
        
        Returns list of validation errors (empty if valid)
        """
        errors = []
        
        if len(input_skins) != 10:
            errors.append(f"Tradeup requires exactly 10 skins, got {len(input_skins)}")
            return errors
        
        # Check that all skins are same rarity
        rarities = set(skin.rarity for skin in input_skins)
        if len(rarities) > 1:
            errors.append(f"All input skins must be same rarity, found: {rarities}")
        
        # Check that all skins are from compatible collections
        # TODO: Implement collection compatibility checking
        
        # Check for StatTrak/Souvenir consistency
        stattrak_count = sum(1 for skin in input_skins if skin.is_stattrak)
        souvenir_count = sum(1 for skin in input_skins if skin.is_souvenir)
        
        if stattrak_count > 0 and stattrak_count != 10:
            errors.append("Either all or no input skins can be StatTrak")
        
        if souvenir_count > 0 and souvenir_count != 10:
            errors.append("Either all or no input skins can be Souvenir")
        
        if stattrak_count > 0 and souvenir_count > 0:
            errors.append("Cannot mix StatTrak and Souvenir skins")
        
        return errors