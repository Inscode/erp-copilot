"""
Tool 1: outstanding_bills
Returns unpaid/partially paid bills with customer contact info.
Supports filtering by business, area, tier, min_days, customer name.
Includes overdue logic based on real business rules:
  CASH   → overdue immediately if unpaid
  CREDIT → overdue after 45 days with no cheque received
"""
from db.database import query


def outstanding_bills(
    business: str = None,
    area: str = None,
    tier: str = None,
    min_days: int = None,
    customer: str = None,
    overdue_only: bool = False
) -> list[dict]:
    """
    Fetch outstanding bills.

    Args:
        business     : RAINCO / PLASTIC / STATIONERY / HARDWARE / RETAIL_SHOP
        area         : Badulla / Welimada / Haputale / Bandarawela / Ella etc.
        tier         : Platinum / Gold / Silver / Bronze / Emergency Top-up
        min_days     : Only bills older than N days
        customer     : Fuzzy search on customer name
        overdue_only : If True, only return overdue bills
    """
    conditions = ["1=1"]
    params = {}

    if business:
        conditions.append("business = :business")
        params["business"] = business.upper()

    if area:
        conditions.append("area ILIKE :area")
        params["area"] = f"%{area}%"

    if tier:
        conditions.append("tier ILIKE :tier")
        params["tier"] = f"%{tier}%"

    if min_days:
        conditions.append("days_since_bill >= :min_days")
        params["min_days"] = min_days

    if customer:
        conditions.append("customer_name ILIKE :customer")
        params["customer"] = f"%{customer}%"

    if overdue_only:
        conditions.append("is_overdue = TRUE")

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            bill_id,
            bill_number,
            customer_name,
            phone,
            area,
            tier,
            shop_type,
            business,
            bill_type,
            bill_date,
            total_amount,
            amount_paid,
            balance_remaining,
            status,
            days_since_bill,
            is_overdue,
            overdue_reason,
            days_overdue
        FROM outstanding_bills_view
        WHERE {where_clause}
        ORDER BY
            -- Overdue bills first
            is_overdue DESC,
            -- Then by overdue reason severity
            CASE overdue_reason
                WHEN 'CHEQUE BOUNCED'       THEN 1
                WHEN 'CASH UNPAID'          THEN 2
                WHEN 'NO CHEQUE RECEIVED'   THEN 3
                ELSE 4
            END,
            -- Then by tier
            CASE tier
                WHEN 'Platinum'         THEN 1
                WHEN 'Gold'             THEN 2
                WHEN 'Silver'           THEN 3
                WHEN 'Bronze'           THEN 4
                WHEN 'Emergency Top-up' THEN 5
                ELSE 6
            END,
            days_overdue DESC
    """

    rows = query(sql, params)

    # Serialize dates
    for row in rows:
        if row.get("bill_date"):
            row["bill_date"] = str(row["bill_date"])

    return rows