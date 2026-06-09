# ERP Copilot

An AI-powered Shop Intelligence Assistant for retail and wholesale businesses.
Ask questions about your business in plain English — get instant answers.

---

## What It Does

Instead of navigating menus and generating reports manually, just ask:

> "Who owes us money in Welimada?"  
> "Which bills have been unpaid for over 45 days?"  
> "Tell me everything about Janalanka Textile"  
> "Who should I call today?"  
> "How is RAINCO doing this month?"  
> "Any bounced cheques?"  

---

## Architecture

    Next.js (Chat UI)
          ↓
    Next.js API Routes
          ↓
    Python FastAPI + LangGraph (AI Agent)
          ↓
    PostgreSQL (direct read)    Spring Boot API (writes)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind |
| Backend | Next.js API Routes |
| AI Orchestration | Python FastAPI + LangGraph |
| LLM | Google Gemini API |
| Database | PostgreSQL + pgvector |
| ORM | Drizzle |
| Automation | n8n (planned) |

---

## Project Structure

    erp-copilot/
    ├── ai-service/          # Python FastAPI + LangGraph agent
    │   ├── agent/           # LangGraph graph and nodes
    │   ├── db/              # PostgreSQL connection
    │   ├── tools/           # Agent tools (one per business question)
    │   ├── main.py          # FastAPI entry point
    │   ├── requirements.txt
    │   └── .env.example
    ├── frontend/            # Next.js chat UI (coming soon)
    ├── scripts/
    │   └── db/
    │       ├── views.sql    # PostgreSQL views for agent queries
    │       └── roles.sql    # Read-only DB user setup
    └── docs/                # Architecture and planning docs

---

## Tools Built

| Tool | What It Answers |
|---|---|
| `outstanding_bills` | Who owes us money, filter by area/tier/business |
| `aging_report` | Outstanding grouped by 0-30, 31-60, 61-90, 90+ days |
| `customer_profile` | Full profile — bills, payments, reminders for one customer |
| `call_list_today` | Prioritized call list based on business rules |

---

## Business Rules

### Bill Types

| Type | Rule |
|---|---|
| CASH | Payment collected immediately on delivery |
| CREDIT | Cheque must be received within 45 days of bill date |

### Bill Status Flow

    CREATED → ASSIGNED → SHOP_WORKER_ASSIGNED → SHOP_RECEIVED → STORE_RECEIVED → COMPLETED
                                                                                → CANCELLED

### Overdue Detection

| Reason | Condition |
|---|---|
| CASH UNPAID | CASH bill, fully_paid = false |
| NO CHEQUE RECEIVED | CREDIT bill, 45+ days, no payment recorded |
| CHEQUE BOUNCED | Payment exists with status = RETURNED |
| MONITORING | CREDIT bill within 45 days, cheque received |

### Customer Tiers

    Platinum → Gold → Silver → Bronze → Emergency Top-up

### Business Units

| Business | Location |
|---|---|
| RAINCO | Store |
| PLASTIC | Store |
| STATIONERY | Store |
| HARDWARE | Store |
| RETAIL_SHOP | Shop |

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Node.js 18+ (for frontend)

### 1. Clone the repo

    git clone https://github.com/yourusername/erp-copilot.git
    cd erp-copilot

### 2. Set up the database

Open pgAdmin and run these scripts in order:

    scripts/db/views.sql    # Creates the 5 views
    scripts/db/roles.sql    # Creates read-only user

### 3. Set up Python service

    cd ai-service
    python -m venv venv
    venv\Scripts\activate        # Windows
    source venv/bin/activate     # Mac/Linux
    pip install -r requirements.txt
    cp .env.example .env
    # Edit .env with your values

### 4. Run the AI service

    uvicorn main:app --reload --port 8000

---

## Roadmap

### Phase 1 — Core Tools ✅
- [x] outstanding_bills
- [x] aging_report
- [x] customer_profile
- [x] call_list_today

### Phase 2 — More Tools
- [ ] bounced_cheques
- [ ] area_report
- [ ] business_summary
- [ ] search_customer
- [ ] customer_payment_behavior
- [ ] pipeline_status (fraud detection — stale ASSIGNED bills)

### Phase 3 — Agent
- [ ] LangGraph agent
- [ ] FastAPI endpoints
- [ ] Chat UI (Next.js)

### Phase 4 — Production
- [ ] Connect to real FMS database
- [ ] Write actions via Spring Boot API
- [ ] Deploy to Render + Vercel

---

## Related Systems

This copilot is designed to sit on top of:

- **FMS** — Finance Management System (Spring Boot + Angular)
- **Ecommerce** — Online store (Spring Boot + Angular)

Both systems remain unchanged. The copilot reads directly
from PostgreSQL and writes only through existing Spring Boot APIs.

---
