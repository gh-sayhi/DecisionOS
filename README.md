# DecisionOS

DecisionOS is an **AI Decision Operating System** for high-stakes business decisions. It helps teams frame the decision, compare options, reason through risk, and produce an executive-ready decision report.

The product is no longer positioned as a vertical content analysis tool. Historical vertical modules remain archived in the codebase for compatibility, but the primary user experience is now DecisionOS.

## Core Positioning

- Product category: AI Decision Operating System
- Primary use case: major decisions before committing budget, people, timing, or strategy
- Main entry: `New Decision`
- Main workspace: `Decision Inputs` + `AI Thinking / Reasoning Timeline` + `Decision Report`
- Output style: enterprise AI advisor, not a generic content generator

## Industry Packs

DecisionOS supports these packs:

- Product
- Startup
- Marketing
- Content
- Hiring
- Investment
- Custom

The Content pack can reuse older content-planning fields as one sample scenario, but it is not the main product.

## Fixed Report Structure

Every generated decision report uses the same executive structure:

1. Executive Summary
2. Decision Verdict
3. Core Value
4. Benchmark
5. Risk Matrix
6. Execution Plan
7. Budget
8. Timeline
9. Next Actions

## Backend Startup

```bash
cd /Users/ruirui/Documents/Codex/2026-06-24/wo-xia/outputs/drama-launch-suite
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Main API:

```text
POST http://127.0.0.1:8001/api/decision/generate
```

## Frontend Startup

```bash
cd /Users/ruirui/Documents/Codex/2026-06-24/wo-xia/outputs/drama-launch-suite/frontend
pnpm build
pnpm start --hostname 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

## Current Routes

```text
http://127.0.0.1:3000           New Decision workspace
http://127.0.0.1:3000/projects  Decision Library
http://127.0.0.1:3000/admin     Admin
http://127.0.0.1:8001/docs      API docs
```

Legacy public entry routes redirect back to the DecisionOS workspace.

## Example Request

```bash
curl -X POST http://127.0.0.1:8001/api/decision/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Launch AI decision workspace",
    "pack": "Product",
    "context": "Enterprise teams need a structured way to make high-stakes decisions from fragmented inputs.",
    "objective": "Decide whether to launch the workspace this quarter.",
    "options": ["Ship focused MVP", "Wait for integrations"],
    "constraints": "Eight week window and limited engineering capacity.",
    "budget": 180000,
    "timeline": "8 weeks",
    "stakeholders": "Product, engineering, sales",
    "success_metrics": "Activation, retention, decision cycle time",
    "known_risks": "Scope may expand too quickly."
  }'
```

## Verification

- `python3 -m compileall backend`
- `pnpm build`
- `GET /`
- `GET /projects`
- `GET /consumer` redirects to `/`
- `POST /api/decision/generate`
