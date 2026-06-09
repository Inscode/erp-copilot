"""
Tool 3: customer_profile
Returns everything about a specific customer.
Answers: "Tell me everything about Janalanka Textile"
         "What does VISVAMS owe us?"
"""
from db.database import query, query_one


def customer_profile(name: str) -> dict:
    """
    Returns full customer profile including all unpaid bills,
    payment history and total outstanding.

    Args:
        name: Customer name — fuzzy matched
    """

    # Step 1 — Find the customer
    customer = query_one("""
        SELECT
            id,
            name,
            phone,
            area,
            tier,
            shop_type,
            active
        FROM customers
        WHERE name ILIKE :name
        LIMIT 1
    """, {"name": f"%{name}%"})

    if not customer:
        return {"error": f"Customer '{name}' not found"}

    customer_id = customer["id"]
    customer_name = customer["name"]

    # Step 2 — Get all unpaid bills
    unpaid_bills = query("""
        SELECT
            bill_id,
            bill_number,
            business,
            bill_date,
            total_amount,
            amount_paid,
            balance_remaining,
            status,
            days_since_bill
        FROM outstanding_bills_view
        WHERE customer_name ILIKE :name
        ORDER BY days_since_bill DESC
    """, {"name": f"%{customer_name}%"})

    # Step 3 — Get payment history
    payment_history = query("""
        SELECT
            p.id            AS payment_id,
            b.bill_number,
            p.amount,
            p.payment_type,
            p.status,
            p.payment_date,
            p.cheque_number,
            p.bank_name,
            p.return_reason
        FROM payments p
        JOIN bills b ON p.bill_id = b.id
        WHERE b.customer_id = :customer_id
           OR b.customer_name ILIKE :name
        ORDER BY p.payment_date DESC
        LIMIT 20
    """, {"customer_id": customer_id, "name": f"%{customer_name}%"})

    # Step 4 — Get total outstanding
    summary = query_one("""
        SELECT
            COUNT(*)                    AS unpaid_bill_count,
            SUM(balance_remaining)      AS total_outstanding,
            MAX(days_since_bill)        AS oldest_unpaid_days,
            MIN(bill_date)              AS oldest_bill_date
        FROM outstanding_bills_view
        WHERE customer_name ILIKE :name
    """, {"name": f"%{customer_name}%"})

    # Step 5 — Get active reminders
    reminders = query("""
        SELECT
            r.reminder_date,
            r.note,
            r.created_by,
            b.bill_number
        FROM bill_reminders r
        JOIN bills b ON r.bill_id = b.id
        WHERE (b.customer_id = :customer_id
           OR b.customer_name ILIKE :name)
          AND b.fully_paid = FALSE
        ORDER BY r.reminder_date DESC
    """, {"customer_id": customer_id, "name": f"%{customer_name}%"})

    # Serialize dates
    for bill in unpaid_bills:
        if bill.get("bill_date"):
            bill["bill_date"] = str(bill["bill_date"])

    for payment in payment_history:
        if payment.get("payment_date"):
            payment["payment_date"] = str(payment["payment_date"])

    for reminder in reminders:
        if reminder.get("reminder_date"):
            reminder["reminder_date"] = str(reminder["reminder_date"])

    return {
        "customer": {
            "name":      customer["name"],
            "phone":     customer["phone"],
            "area":      customer["area"],
            "tier":      customer["tier"],
            "shop_type": customer["shop_type"],
            "active":    customer["active"]
        },
        "summary": {
            "unpaid_bill_count":  summary["unpaid_bill_count"],
            "total_outstanding":  float(summary["total_outstanding"] or 0),
            "oldest_unpaid_days": summary["oldest_unpaid_days"],
            "oldest_bill_date":   str(summary["oldest_bill_date"]) if summary["oldest_bill_date"] else None
        },
        "unpaid_bills":    unpaid_bills,
        "payment_history": payment_history,
        "reminders":       reminders
    }