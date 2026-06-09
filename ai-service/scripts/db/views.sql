
-- ============================================================
-- Read-only user for ERP Copilot Python service
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles
        WHERE rolname = 'copilot_reader'
    ) THEN
        CREATE USER copilot_reader WITH PASSWORD 'change_this_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE your_db_name TO copilot_reader;
GRANT USAGE ON SCHEMA public TO copilot_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO copilot_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO copilot_reader;


-- ============================================================
-- View 1: Outstanding bills with overdue logic
-- ============================================================
CREATE OR REPLACE VIEW outstanding_bills_view AS
SELECT
    b.id                                        AS bill_id,
    b.bill_number,
    b.customer_name,
    c.phone,
    COALESCE(c.area, b.area)                    AS area,
    c.tier,
    c.shop_type,
    b.business,
    b.division,
    b.bill_type,
    b.bill_date,
    b.total_amount,
    b.amount_paid,
    b.balance_remaining,
    b.status,
    (CURRENT_DATE - b.bill_date)                AS days_since_bill,

    CASE
        WHEN b.bill_type = 'CASH'
         AND b.fully_paid = FALSE
            THEN TRUE
        WHEN b.bill_type = 'CREDIT'
         AND (CURRENT_DATE - b.bill_date) > 45
         AND NOT EXISTS (
             SELECT 1 FROM payments p
             WHERE p.bill_id = b.id
               AND p.status != 'RETURNED'
         )
            THEN TRUE
        ELSE FALSE
    END                                         AS is_overdue,

    CASE
        WHEN b.bill_type = 'CASH'
         AND b.fully_paid = FALSE
            THEN 'CASH UNPAID'
        WHEN b.bill_type = 'CREDIT'
         AND (CURRENT_DATE - b.bill_date) > 45
         AND NOT EXISTS (
             SELECT 1 FROM payments p
             WHERE p.bill_id = b.id
               AND p.status != 'RETURNED'
         )
            THEN 'NO CHEQUE RECEIVED'
        WHEN b.bill_type = 'CREDIT'
         AND EXISTS (
             SELECT 1 FROM payments p
             WHERE p.bill_id = b.id
               AND p.status = 'RETURNED'
         )
            THEN 'CHEQUE BOUNCED'
        ELSE 'MONITORING'
    END                                         AS overdue_reason,

    CASE
        WHEN b.bill_type = 'CASH'
            THEN (CURRENT_DATE - b.bill_date)
        WHEN b.bill_type = 'CREDIT'
            THEN GREATEST((CURRENT_DATE - b.bill_date) - 45, 0)
        ELSE 0
    END                                         AS days_overdue

FROM bills b
LEFT JOIN customers c ON b.customer_id = c.id
WHERE b.fully_paid = FALSE
  AND b.status NOT IN ('CANCELLED', 'CREATED', 'ASSIGNED');


-- ============================================================
-- View 2: Bounced cheques
-- ============================================================
CREATE OR REPLACE VIEW bounced_cheques_view AS
SELECT
    p.id                AS payment_id,
    p.bill_id,
    b.customer_name,
    c.phone,
    c.area,
    c.tier,
    b.business,
    p.cheque_number,
    p.bank_name,
    p.branch_name,
    p.amount,
    p.cheque_date,
    p.return_reason,
    p.payment_date      AS bounce_date
FROM payments p
JOIN bills b        ON p.bill_id = b.id
LEFT JOIN customers c ON b.customer_id = c.id
WHERE p.payment_type = 'CHEQUE'
  AND p.status = 'RETURNED';


-- ============================================================
-- View 3: Overdue reminders
-- ============================================================
CREATE OR REPLACE VIEW overdue_reminders_view AS
SELECT
    r.id                                        AS reminder_id,
    r.bill_id,
    b.customer_name,
    c.phone,
    c.area,
    c.tier,
    b.business,
    b.bill_number,
    r.reminder_date,
    r.note,
    b.balance_remaining,
    b.fully_paid,
    (CURRENT_DATE - r.reminder_date)            AS days_past_reminder
FROM bill_reminders r
JOIN bills b        ON r.bill_id = b.id
LEFT JOIN customers c ON b.customer_id = c.id
WHERE r.reminder_date < CURRENT_DATE
  AND b.fully_paid = FALSE;


-- ============================================================
-- View 4: Business summary
-- ============================================================
CREATE OR REPLACE VIEW business_summary_view AS
SELECT
    b.business,
    COUNT(*)                                    AS total_unpaid_bills,
    SUM(b.balance_remaining)                    AS total_outstanding,
    MAX(CURRENT_DATE - b.bill_date)             AS oldest_unpaid_days,
    MIN(b.bill_date)                            AS oldest_bill_date,
    SUM(CASE WHEN b.is_overdue THEN 1 ELSE 0 END) AS overdue_count,
    SUM(CASE WHEN b.is_overdue
        THEN b.balance_remaining ELSE 0 END)    AS overdue_amount
FROM outstanding_bills_view b
GROUP BY b.business;


-- ============================================================
-- View 5: Area summary
-- ============================================================
CREATE OR REPLACE VIEW area_summary_view AS
SELECT
    area,
    COUNT(*)                                    AS unpaid_bill_count,
    SUM(balance_remaining)                      AS total_outstanding,
    MAX(days_since_bill)                        AS oldest_days,
    COUNT(DISTINCT customer_name)               AS customer_count,
    SUM(CASE WHEN is_overdue THEN 1 ELSE 0 END) AS overdue_count
FROM outstanding_bills_view
GROUP BY area;