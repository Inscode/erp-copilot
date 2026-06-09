"""
Tool 2: aging_report
Groups outstanding bills into age buckets per business.
Answers: "How is Rainco doing?", "Which business has the oldest debts?"
"""
from db.database import query


def aging_report(business: str = None) -> dict:
    """
    Returns outstanding bills grouped into aging buckets.

    Args:
        business: Optional filter — RAINCO / PLASTIC / STATIONERY / HARDWARE / RETAIL_SHOP
                  If None, returns all businesses.
    """
    params = {}
    business_filter = ""

    if business:
        business_filter = "AND business = :business"
        params["business"] = business.upper()

    sql = f"""
        SELECT
            business,
            SUM(CASE WHEN days_since_bill BETWEEN 0  AND 30
                THEN 1 ELSE 0 END)                          AS count_0_30,
            SUM(CASE WHEN days_since_bill BETWEEN 0  AND 30
                THEN balance_remaining ELSE 0 END)          AS amount_0_30,

            SUM(CASE WHEN days_since_bill BETWEEN 31 AND 60
                THEN 1 ELSE 0 END)                          AS count_31_60,
            SUM(CASE WHEN days_since_bill BETWEEN 31 AND 60
                THEN balance_remaining ELSE 0 END)          AS amount_31_60,

            SUM(CASE WHEN days_since_bill BETWEEN 61 AND 90
                THEN 1 ELSE 0 END)                          AS count_61_90,
            SUM(CASE WHEN days_since_bill BETWEEN 61 AND 90
                THEN balance_remaining ELSE 0 END)          AS amount_61_90,

            SUM(CASE WHEN days_since_bill > 90
                THEN 1 ELSE 0 END)                          AS count_90_plus,
            SUM(CASE WHEN days_since_bill > 90
                THEN balance_remaining ELSE 0 END)          AS amount_90_plus,

            COUNT(*)                                        AS total_bills,
            SUM(balance_remaining)                          AS total_outstanding,
            MAX(days_since_bill)                            AS oldest_days
        FROM outstanding_bills_view
        WHERE 1=1 {business_filter}
        GROUP BY business
        ORDER BY total_outstanding DESC
    """

    rows = query(sql, params)

    # Format into clean nested structure
    result = {}
    for row in rows:
        result[row["business"]] = {
            "0_30_days": {
                "count":  row["count_0_30"],
                "amount": float(row["amount_0_30"] or 0)
            },
            "31_60_days": {
                "count":  row["count_31_60"],
                "amount": float(row["amount_31_60"] or 0)
            },
            "61_90_days": {
                "count":  row["count_61_90"],
                "amount": float(row["amount_61_90"] or 0)
            },
            "90_plus_days": {
                "count":  row["count_90_plus"],
                "amount": float(row["amount_90_plus"] or 0)
            },
            "total_bills":       row["total_bills"],
            "total_outstanding": float(row["total_outstanding"] or 0),
            "oldest_days":       row["oldest_days"]
        }

    return result