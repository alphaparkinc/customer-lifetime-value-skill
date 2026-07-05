"""
example_usage.py -- Demonstrates CustomerLifetimeValueClient
"""
from client import CustomerLifetimeValueClient

def main():
    client = CustomerLifetimeValueClient()
    result = client.calculate_clv(
        avg_order_value=65.00,
        purchase_frequency_yearly=4.5,
        churn_rate_yearly=0.25
    )
    print("[Customer Lifetime Value Analysis]")
    print(f"Avg Lifespan: {result['lifespan_years']} years")
    print(f"LTV (Lifespan): ${result['historical_clv_usd']}")
    print(f"3-Yr Value (discounted): ${result['projected_clv_3yr_usd']}")
    print(f"Max Acquisition Budget: ${result['recommended_cac_max_usd']}")

if __name__ == "__main__":
    main()
