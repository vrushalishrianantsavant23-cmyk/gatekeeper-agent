# Gatekeeper-agent
Instagram commerce agent with agentic memory and a verifier gate before CRM/ERP writes.
# Gatekeeper Agent

An Instagram DM commerce agent concept where every proposed action — creating
an order, updating a customer record — must be independently verified against
live business data before it's allowed to execute. Built around the idea that
an AI agent talking to a customer should never have direct write access to a
business's CRM/ERP; a separate verification step sits in between.

## What's actually built and working

- **CRM/ERP data layer** (`crm-erp/`) — a live PostgreSQL database (hosted on
  Supabase) with contacts, deals, activities, products, orders, order_items,
  and invoices tables. Seeded with sample data and verified working.
- **Data access layer** (`crm-erp/db.py`) — functions to read/write against
  that database, including an atomic, stock-safe `create_order` transaction.
  Tested live against the real database.
- **Verifier** (`verifier/verify_order.py`) — takes a proposed order and
  checks it against real stock levels and known contacts before approving it.
  Rejects orders for unknown products, unknown customers, or insufficient
  stock, with a clear reason for each rejection. This is the core idea of the
  project in its simplest working form.

## What's designed, not yet built

- **Agentic memory** — instead of static document retrieval (RAG), each
  customer's preferences, budget, and history would be held as evolving,
  linked notes that get superseded and connected over time, rather than
  re-retrieved from scratch each conversation.
- **Instagram integration (n8n + ManyChat)** — the actual DM ingestion layer
  that would route messages to the agent.
- **Evaluation harness** — a labeled test set measuring verifier accuracy,
  correct escalation, and hallucination rate against a no-verifier baseline.

This project prioritizes shipping one real, working, tested piece —
the verification gate — over a larger set of half-built features.

## Stack

PostgreSQL (Supabase), Python (psycopg2)

## Why this approach

Most AI customer-service demos let the model reply directly, sometimes with
retrieval bolted on. The open question that matters more, once an agent can
actually take actions (create an order, update a record), is what stops it
from acting on bad information — a hallucinated price, an out-of-stock item,
an unknown customer. This project's answer: nothing gets written to the
business's real data unless a separate check confirms it against that data
first.
