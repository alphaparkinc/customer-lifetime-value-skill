"""
example_usage.py -- Demonstrates the CLVClient SDK.
"""
from client import CLVClient
from datetime import date, timedelta
import random

def generate_sample_orders(n_customers=50, n_orders=200, seed=42):
    random.seed(seed)
    orders = []
    base_date = date(2024, 1, 1)
    for _ in range(n_orders):
        customer_id = f"C{random.randint(1, n_customers):04d}"
        days_ago = random.randint(0, 365)
        amount = round(random.uniform(20, 500), 2)
        order_date = base_date + timedelta(days=days_ago)
        orders.append({"customer_id": customer_id, "amount": amount, "date": str(order_date)})
    return orders

def main():
    client = CLVClient(prediction_months=12, segment_count=4)
    orders = generate_sample_orders()

    print("[CLV Analysis]")
    result = client.analyze(orders)

    s = result["summary"]
    print(f"\nSummary:")
    print(f"  Total Customers:  {s['total_customers']}")
    print(f"  Total Revenue:    ${s['total_revenue']:,.2f}")
    print(f"  Avg Order Value:  ${s['avg_order_value']:,.2f}")
    print(f"  Avg Predicted CLV (12mo): ${s['avg_predicted_clv']:,.2f}")

    print(f"\nCustomer Segments:")
    for seg_name, stats in result["segments"].items():
        print(f"  {seg_name:<20} | Customers: {stats['customer_count']:>3} | Avg CLV: ${stats['avg_predicted_clv']:>8,.2f} | Avg Orders: {stats['avg_order_count']}")

    print(f"\nTop 5 Customers by Predicted CLV:")
    for c in result["top_customers"][:5]:
        print(f"  {c['customer_id']} | Segment: {c['segment']:<20} | CLV: ${c['predicted_clv']:>8,.2f} | Orders: {c['order_count']} | Spent: ${c['total_spent']:,.2f}")

if __name__ == "__main__":
    main()
