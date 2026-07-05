# customer-lifetime-value-skill

> **GenPark AI Agent Skill** -- CLV / LTV cohort analyzer and CAC boundary advisor.

## Quick Start

```python
from client import CustomerLifetimeValueClient
client = CustomerLifetimeValueClient()
res = client.calculate_clv(80.00, 3.0, 0.3)
print(res["historical_clv_usd"])
```
