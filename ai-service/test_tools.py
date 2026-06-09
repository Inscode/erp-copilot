import sys
sys.path.append(".")

from tools.outstanding_bills import outstanding_bills
from tools.aging_report import aging_report
from tools.customer_profile import customer_profile
from tools.call_list_today import call_list_today

print("\n=== Tool 1: Outstanding Bills ===")
bills = outstanding_bills()
print(f"Total outstanding bills: {len(bills)}")
for b in bills[:3]:
    print(f"  {b['bill_number']} | {b['customer_name']} | LKR {b['balance_remaining']} | {b['overdue_reason']}")

print("\n=== Tool 1b: Overdue Only ===")
overdue = outstanding_bills(overdue_only=True)
print(f"Total overdue bills: {len(overdue)}")

print("\n=== Tool 1c: Filter by Business ===")
rainco = outstanding_bills(business="RAINCO")
print(f"RAINCO outstanding: {len(rainco)}")

print("\n=== Tool 2: Aging Report ===")
aging = aging_report()
for business, data in aging.items():
    print(f"  {business}: LKR {data['total_outstanding']} | oldest: {data['oldest_days']} days")

print("\n=== Tool 3: Customer Profile ===")
profile = customer_profile("Janalanka")
print(f"  Customer: {profile['customer']['name']}")
print(f"  Total outstanding: LKR {profile['summary']['total_outstanding']}")
print(f"  Unpaid bills: {profile['summary']['unpaid_bill_count']}")

print("\n=== Tool 4: Call List Today ===")
calls = call_list_today()
print(f"Total calls today: {len(calls)}")
for c in calls[:5]:
    print(f"  [{c['call_reason']}] {c['customer_name']} | LKR {c['balance_remaining']}")

print("\n✅ All tools working!")