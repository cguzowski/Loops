# Template use

Master creates plans/intake/tasks/contracts and initial worker records. Once
handed off, each worker owns its record; QA owns its reports. Replace placeholders
with confirmed values or explicit unknowns; drafts do not authorize execution.

| Template | Live location | Writer |
| --- | --- | --- |
| [SUBAGENT.md](SUBAGENT.md) | `agents/<ID>/AGENT.md` | Named worker after one-time initialization |
| [PLAN.md](PLAN.md) | `plans/<PLAN-ID>-v<revision>.md` | Master; freeze published revisions |
| [JIRA_ITEM.md](JIRA_ITEM.md) | `work-items/<KEY>.md` | Master |
| [TASK.md](TASK.md) | `tasks/<TASK-ID>.md` | Master |
| [CONTRACT.md](CONTRACT.md) | `contracts/<CON-ID>-v<revision>.md` | Master; freeze agreed revisions |
| [QA_REPORT.md](QA_REPORT.md) | `agents/<QA-AGENT-ID>/archive/<REPORT-ID>-v<revision>.md` | Assigned QA agent; Master reserves report identity |
| [QA.md](QA.md) | Reference from QA charter/launch | Specialization procedure |
| [INTEGRATION.md](INTEGRATION.md) | Reference from integration charter/launch | Specialization procedure |

Store immutable selected requirements as work-items/<KEY>-r<n>.json.
Create record folders as needed. Registry carries envelope metadata, not duplicate
editable user requirements; see [REGISTRY_GUIDE.md](../REGISTRY_GUIDE.md).
Load templates explicitly through role records and launch prompts.
Master allocates plan/task/contract IDs and globally unique QA report revisions.
User/UserAssistant allocates USER request/decision IDs. These are separate from
stable agent IDs; submitted report/plan revisions are never overwritten.

Domain/layer axes aid navigation; permissions remain one owner per actual path.
Add an agent when real responsibility justifies it, not for hypothetical SaaS
domains. QA specializes in independent verification and has owns: [].
