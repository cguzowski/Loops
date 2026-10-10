# Context and navigation index

Writer: MasterAgent. Load only sources relevant to your role and assignment.

| Need | Source | Use |
| --- | --- | --- |
| Ownership, TDD, concurrency | [POLICY.md](POLICY.md) | Startup and affected changes |
| Delivery stages/approval/QA | [JIRA_WORKFLOW.md](JIRA_WORKFLOW.md) | Current gates |
| Actual Jira/runner setup | [JIRA_SETUP.md](JIRA_SETUP.md) | Confirm integration state and gaps |
| Standing user direction | [USER.md](communication/USER.md) | Global facts/decisions; never edit as Master/worker |
| Master questions/routing/verdicts | [MASTER.md](communication/MASTER.md) | Relevant coordination |
| Owners/internal tasks/local receipts | [REGISTRY.json](REGISTRY.json) | Query relevant agent/task/work item |
| Current product requests/decisions | Actual Jira item/comments | Fetch current source; snapshots are receipts |
| Intake / selected requirements | work_items entry → work-items/<KEY>.md and immutable JSON | Approved intent and change delta |
| Plan | work_items entry → plans/<PLAN-ID>-v<revision>.md | Exact approved revision |
| Source map and safe commands | [PROJECT.md](PROJECT.md) | Verify paths/symbols at assigned SHA |
| Terms/search aliases | [GLOSSARY.md](GLOSSARY.md) | Resolve owner and source |
| Enduring decisions | [DECISIONS.md](DECISIONS.md) | Check authority and scope |
| Bounded task | tasks entry → tasks/<TASK-ID>.md | Acceptance/context |
| Boundary agreement | contracts entry → contracts/<CON-ID>-v<revision>.md | Pinned producer/consumer expectations |
| Worker / QA evidence | agents entry → agents/<ID>/AGENT.md, own archive | Relevant receipts/reports only |
| New records | [templates/README.md](templates/README.md) | Correct template/writer |
| Session startup | [LAUNCH_PROMPTS.md](LAUNCH_PROMPTS.md) | Explicit role and absolute roots |
| Guards | [tools/README.md](tools/README.md) | Readiness/workflow/source-scope checks |

## Navigation

Resolve business term/technical asset → owner → actual entry point and tests →
approved plan/contract → source at assigned revision. Report missing/ambiguous
routes rather than inventing components. Use durable paths and symbols.
Owners propose navigation updates; Master verifies and applies them.
