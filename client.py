"""
customer-lifetime-value-skill: Client SDK
Calculate, predict, and segment customers by Lifetime Value (CLV) using RFM analysis.
"""

from __future__ import annotations
import math
from datetime import datetime, date, timedelta
from typing import Optional
from collections import defaultdict


SEGMENT_LABELS = {
    4: "Champions",
    3: "Loyal Customers",
    2: "At Risk",
    1: "Lost / Inactive",
}


class CLVClient:
    """
    SDK for Customer Lifetime Value calculation and segmentation.

    Uses RFM (Recency, Frequency, Monetary) scoring combined with
    a simplified BG/NBD-inspired CLV projection.

    Methods:
        analyze(orders)            - Full CLV analysis pipeline
        rfm_score(customer_data)   - Compute RFM scores
        predict_clv(customer_data) - Project future revenue
        segment(customers)         - Group customers into value tiers
    """

    def __init__(self, prediction_months: int = 12, segment_count: int = 4):
        self.prediction_months = prediction_months
        self.segment_count = min(max(segment_count, 2), 5)

    def analyze(self, orders: list[dict]) -> dict:
        """
        Full CLV analysis pipeline.

        Args:
            orders: List of dicts with keys:
                    - customer_id (str)
                    - amount (float) — order value
                    - date (str) — ISO format e.g. "2024-03-15"

        Returns:
            dict with keys: customers, segments, top_customers, summary
        """
        if not orders:
            return {"customers": [], "segments": {}, "top_customers": [], "summary": {}}

        # Parse and group orders by customer
        customer_orders = self._group_by_customer(orders)
        reference_date = self._get_reference_date(orders)

        # Build customer records
        customers = []
        for cid, corders in customer_orders.items():
            record = self._build_customer_record(cid, corders, reference_date)
            customers.append(record)

        # RFM scoring
        customers = self._score_rfm(customers)

        # CLV prediction
        for c in customers:
            c["predicted_clv"] = self._predict_clv(c)

        # Segmentation
        customers = self._segment_customers(customers)

        # Build segment summary
        segments = self._summarize_segments(customers)

        # Top customers by predicted CLV
        top_customers = sorted(customers, key=lambda x: x["predicted_clv"], reverse=True)[:10]

        summary = {
            "total_customers": len(customers),
            "total_revenue": round(sum(c["total_spent"] for c in customers), 2),
            "avg_order_value": round(sum(c["avg_order_value"] for c in customers) / len(customers), 2),
            "avg_predicted_clv": round(sum(c["predicted_clv"] for c in customers) / len(customers), 2),
            "prediction_months": self.prediction_months,
            "reference_date": str(reference_date),
        }

        return {
            "customers": customers,
            "segments": segments,
            "top_customers": top_customers,
            "summary": summary,
        }

    def _group_by_customer(self, orders: list[dict]) -> dict:
        grouped = defaultdict(list)
        for order in orders:
            cid = str(order.get("customer_id", "unknown"))
            try:
                amount = float(order.get("amount", 0))
                raw_date = order.get("date", "")
                if isinstance(raw_date, str):
                    order_date = datetime.fromisoformat(raw_date.split("T")[0]).date()
                elif isinstance(raw_date, (datetime,)):
                    order_date = raw_date.date()
                elif isinstance(raw_date, date):
                    order_date = raw_date
                else:
                    continue
                grouped[cid].append({"amount": amount, "date": order_date})
            except (ValueError, TypeError):
                continue
        return grouped

    def _get_reference_date(self, orders: list[dict]) -> date:
        dates = []
        for o in orders:
            try:
                raw = o.get("date", "")
                if isinstance(raw, str):
                    dates.append(datetime.fromisoformat(raw.split("T")[0]).date())
            except ValueError:
                pass
        return max(dates) if dates else date.today()

    def _build_customer_record(
        self, customer_id: str, orders: list[dict], reference_date: date
    ) -> dict:
        """Build base metrics for a customer."""
        amounts = [o["amount"] for o in orders]
        dates = sorted(o["date"] for o in orders)

        recency_days = (reference_date - dates[-1]).days
        frequency = len(orders)
        monetary = sum(amounts)
        avg_order_value = monetary / frequency if frequency > 0 else 0

        # Inter-purchase intervals
        intervals = []
        for i in range(1, len(dates)):
            intervals.append((dates[i] - dates[i - 1]).days)
        avg_interval = sum(intervals) / len(intervals) if intervals else 365

        return {
            "customer_id": customer_id,
            "order_count": frequency,
            "total_spent": round(monetary, 2),
            "avg_order_value": round(avg_order_value, 2),
            "first_order_date": str(dates[0]),
            "last_order_date": str(dates[-1]),
            "recency_days": recency_days,
            "avg_purchase_interval_days": round(avg_interval, 1),
            "rfm_r": 0,
            "rfm_f": 0,
            "rfm_m": 0,
            "rfm_score": 0,
            "predicted_clv": 0.0,
            "segment": "Unknown",
        }

    def _score_rfm(self, customers: list[dict]) -> list[dict]:
        """Assign 1-4 RFM scores using quartile ranking."""
        def quartile_rank(values: list[float], val: float, reverse: bool = False) -> int:
            sorted_vals = sorted(set(values))
            n = len(sorted_vals)
            if n < 4:
                return 4 if (val == max(values)) != reverse else 1
            q1 = sorted_vals[n // 4]
            q2 = sorted_vals[n // 2]
            q3 = sorted_vals[3 * n // 4]
            if reverse:  # Lower is better (recency)
                if val <= q1: return 4
                if val <= q2: return 3
                if val <= q3: return 2
                return 1
            else:  # Higher is better
                if val >= q3: return 4
                if val >= q2: return 3
                if val >= q1: return 2
                return 1

        recencies = [c["recency_days"] for c in customers]
        frequencies = [c["order_count"] for c in customers]
        monetaries = [c["total_spent"] for c in customers]

        for c in customers:
            c["rfm_r"] = quartile_rank(recencies, c["recency_days"], reverse=True)
            c["rfm_f"] = quartile_rank(frequencies, c["order_count"])
            c["rfm_m"] = quartile_rank(monetaries, c["total_spent"])
            c["rfm_score"] = round((c["rfm_r"] + c["rfm_f"] + c["rfm_m"]) / 3, 2)

        return customers

    def _predict_clv(self, customer: dict) -> float:
        """
        Simplified CLV prediction using historical purchase rate.
        CLV = (avg_order_value * purchase_frequency_per_month) * prediction_months * retention_factor
        """
        avg_interval = customer["avg_purchase_interval_days"]
        if avg_interval <= 0:
            avg_interval = 365

        purchases_per_month = 30.44 / avg_interval
        # Retention factor: higher RFM score = better retention
        retention_factor = 0.3 + (customer["rfm_score"] / 4) * 0.7
        clv = customer["avg_order_value"] * purchases_per_month * self.prediction_months * retention_factor
        return round(clv, 2)

    def _segment_customers(self, customers: list[dict]) -> list[dict]:
        """Assign segment labels based on RFM score quartiles."""
        scores = sorted([c["rfm_score"] for c in customers])
        n = len(scores)
        thresholds = [scores[max(0, int(n * i / self.segment_count) - 1)] for i in range(1, self.segment_count)]

        for c in customers:
            score = c["rfm_score"]
            tier = 1
            for t in thresholds:
                if score >= t:
                    tier += 1
            tier = min(tier, 4)
            c["segment"] = SEGMENT_LABELS.get(tier, f"Tier {tier}")

        return customers

    def _summarize_segments(self, customers: list[dict]) -> dict:
        """Build segment summary statistics."""
        seg_data: dict[str, list] = defaultdict(list)
        for c in customers:
            seg_data[c["segment"]].append(c)

        summary = {}
        for seg_name, members in seg_data.items():
            clvs = [m["predicted_clv"] for m in members]
            summary[seg_name] = {
                "customer_count": len(members),
                "avg_predicted_clv": round(sum(clvs) / len(clvs), 2),
                "total_predicted_clv": round(sum(clvs), 2),
                "avg_order_count": round(sum(m["order_count"] for m in members) / len(members), 1),
                "avg_rfm_score": round(sum(m["rfm_score"] for m in members) / len(members), 2),
            }
        return summary
