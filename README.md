# customer-lifetime-value-skill

> **GenPark AI Agent Skill** — Calculate, predict, and segment customers by Lifetime Value using RFM analysis.

## Overview

Implements a full CLV analysis pipeline: RFM scoring (Recency, Frequency, Monetary), CLV projection, and customer segmentation into Champions, Loyal Customers, At Risk, and Lost tiers.

## Quick Start

```python
from client import CLVClient

client = CLVClient(prediction_months=12)
result = client.analyze(orders)  # orders = [{customer_id, amount, date}]

print(result["summary"])
for seg, stats in result["segments"].items():
    print(f"{seg}: {stats['customer_count']} customers, avg CLV ${stats['avg_predicted_clv']:.2f}")
```

## Segments

| Segment | Description |
|---------|-------------|
| Champions | Recent buyers, high frequency, high spend |
| Loyal Customers | Regular buyers with good value |
| At Risk | Previously active, now lapsing |
| Lost / Inactive | No recent activity, low scores |

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
