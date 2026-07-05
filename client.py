"""
customer-lifetime-value-skill: Client SDK
Estimates historical and projected CLV along with sustainable CAC boundaries.
"""
from __future__ import annotations
from typing import Optional


class CustomerLifetimeValueClient:
    """
    SDK for CLV and LTV analytics.
    """

    def calculate_clv(
        self,
        avg_order_value: float,
        purchase_frequency_yearly: float,
        churn_rate_yearly: float,
    ) -> dict:
        # Prevent division by zero
        churn = max(0.01, min(churn_rate_yearly, 1.0))
        
        # Average lifespan in years is 1 / churn_rate
        lifespan_years = 1.0 / churn
        
        # Historical CLV = AOV * Freq * Lifespan
        historical_clv = avg_order_value * purchase_frequency_yearly * lifespan_years

        # 3 Year Projected CLV (with simple NPV discount factor of 10% per year)
        clv_3yr = 0.0
        for y in range(3):
            survival_prob = (1 - churn) ** y
            discount_factor = 1.10 ** y
            yearly_value = avg_order_value * purchase_frequency_yearly
            clv_3yr += (yearly_value * survival_prob) / discount_factor

        # Standard healthy CAC limit is 1/3 of CLV
        max_cac = historical_clv / 3.0

        return {
            "lifespan_years": round(lifespan_years, 1),
            "historical_clv_usd": round(historical_clv, 2),
            "projected_clv_3yr_usd": round(clv_3yr, 2),
            "recommended_cac_max_usd": round(max_cac, 2),
        }
