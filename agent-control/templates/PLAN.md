# PLAN-<ID> — <Jira key and observable outcome>

Plan ID: PLAN-<ID>
Revision: <n>
Writer: MasterAgent. Freeze published revisions; changes need a new revision/file.

## Understanding for the user

- Jira source: <key/link and selected requirement revision/digest>
- What changed: <specific intent delta or initial request>
- Intended outcome: <interpretation and acceptance examples>
- Existing behavior / affected systems: <actual source/contract references>
- Constraints and assumptions: <confirmed limits; label assumptions>
- Questions needing an answer: <specific or none>

## Proposed work

| Task / owner | Bounded deliverable | Dependency / interface | Acceptance and verification |
| --- | --- | --- | --- |
| <TASK-ID / agent> | <observable outcome and actual scope> | <pinned source/contract> | <AC IDs / actual profiles> |

Include workspace/integration tasks when needed; independent QA is required for
every delivery. Explain the smallest clear
implementation, TDD, regressions, and relevant failure cases. Link detail instead
of duplicating source or registry state.

## Delivery and QA

- Completion target: <local or promoted; actual target branch/base if promoted>
- Promotion authority requested: <explicit narrow clause or none; deployment separate>
- Independent QA owner/checks: <agent, profiles, user-visible preview/demo>
- Final user decision: Required after current QA report; pass alone is not Done.
- Material risks/gaps: <specific or none>
- Epic/child scope: <current scoped children; parked children remain parked>

## Decision requested

Approve in Jira with `APPROVE PLAN-<ID>@<revision>`, or reply with changes/questions.
This approves only the documented scope/conditions and selected request snapshot.
Work stays Backlog until approval.

- Published Jira comment / UTC: <actual reference>
- Human decision receipt: <author account/comment ID/exact bindings, or pending>
- Supersedes: <previous revision or none>
