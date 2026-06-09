"""
Tool 4: call_list_today
Returns prioritized list of customers to call today.
Uses real business rules:
  CASH bills   → should be collected immediately
  CREDIT bills → cheque must be received within 45 days
"""
from db.database import query


def call_list_today() -> list[dict]:
    """
    Returns today's call list sorted by priority.

    Priority:
    1. CHEQUE BOUNCED    → urgent, needs immediate recovery
    2. CASH UNPAID       → should have been collected on delivery
    3. NO CHEQUE RECEIVED → credit bill past 45 days, no cheque handed over
    4. REMINDER DUE      → manual reminder set by accountant

    Within each priority, sorted by tier:
    Platinum → Gold → Silver → Bronze → Emergency Top-up
    """

    # Priority 1 + 2 + 3 — Bills flagged as overdue by business rules
    overdue_bills = query("""
        SELECT
            overdue_reason                  AS call_reason,
            customer_name,
            phone,
            area,
            tier,
            business,
            bill_number,
            bill_type,
            bill_date,
            balance_remaining,
            days_since_bill,
            days_overdue,
            NULL::date                      AS reminder_date,
            NULL                            AS reminder_note
        FROM outstanding_bills_view
        WHERE is_overdue = TRUE
        ORDER BY
            -- Priority by overdue reason
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
    """)

    # Priority 4 — Manual reminders set by accountant that are now due
    reminder_calls = query("""
        SELECT
            'REMINDER DUE'                  AS call_reason,
            r.customer_name,
            r.phone,
            r.area,
            r.tier,
            r.business,
            r.bill_number,
            NULL                            AS bill_type,
            NULL::date                      AS bill_date,
            r.balance_remaining,
            NULL::integer                   AS days_since_bill,
            NULL::integer                   AS days_overdue,
            r.reminder_date,
            r.note                          AS reminder_note
        FROM overdue_reminders_view r
        WHERE r.bill_number NOT IN (
            SELECT bill_number
            FROM outstanding_bills_view
            WHERE is_overdue = TRUE
        )
        ORDER BY
            CASE r.tier
                WHEN 'Platinum'         THEN 1
                WHEN 'Gold'             THEN 2
                WHEN 'Silver'           THEN 3
                WHEN 'Bronze'           THEN 4
                WHEN 'Emergency Top-up' THEN 5
                ELSE 6
            END,
            r.days_past_reminder DESC
    """)

    # Combine — overdue first, then reminders
    all_calls = overdue_bills + reminder_calls

    # Serialize dates
    for call in all_calls:
        for field in ["bill_date", "reminder_date"]:
            if call.get(field):
                call[field] = str(call[field])

    return all_calls