# <AGENT-ID> operating record

Writer: <AGENT-ID> after Master's one-time initialization.
Record revision: 1

## Charter — confirm against registry

- Agent ID: <stable lowercase ID>
- Charter revision acknowledged: <registry charter_revision>
- Product domains: <business responsibilities, if any>
- Technical layers: <technical responsibilities, if any>
- Business outcome owned: <brief; do not invent product requirements>
- Source write scopes: Read REGISTRY.json; do not keep a separate permission list.
- Public boundaries: <contract IDs and source symbols>
- Exclusions / adjacent owners: <specific routing references>
- Role specialization: <implementation / integration / tooling / qa>

Follow `CONTROL_ROOT/POLICY.md`. Master assigns work and reviews results. Read
peers' relevant code and reports, but never edit their files. Report charter
changes for Master to authorize in the registry; then update your own record.

## Operating procedure

1. Establish AGENT_ID, TASK_ID, SESSION_ID, CODE_ROOT, and live CONTROL_ROOT.
   Read INDEX, policy, your selected registry envelope, task criteria, and pinned
   contracts, JIRA_WORKFLOW, and the linked current approved plan/request snapshot.
   Confirm genuine approval bindings and the appropriate Jira stage; no execution
   in Archive/Backlog. Confirm one live session for your agent ID and task; conflicting
   session receipts require a Master-confirmed handoff before edits.
2. Confirm the actual branch/worktree and base commit match the assignment.
   Read relevant Jira once at this new/resumed session startup, or obtain a
   fresh Master reconciliation if your read access is unavailable. Route findings;
   no Jira writes or recurring checks during implementation. Use live local
   assignment re-reads below between the allowed synchronization windows.
   Inspect status and preserve existing work. Read applicable source instructions
   and search actual code/tests for existing implementations and patterns.
   The reconciliation must be for this launch and bind UTC, issue key, current
   requirement digest and approved plan. Missing current evidence pauses writes.
3. Acknowledge the current task/charter/policy/contract revisions below. Re-check
   live readiness and dependencies before edits. Do not expand your path scopes.
4. Write a short plan for the smallest coherent change. For behavior changes,
   use red → green → refactor and retain meaningful evidence. Do not weaken tests.
   For a workspace task, create only declared branches/worktrees at pinned bases;
   inspect setup outputs instead of changing source behavior. For QA, read QA.md,
   perform independent verification only, and write your own report; no source edits.
5. At phase boundaries, re-read assignment revision/cancellation and relevant
   contract state. Stop and checkpoint when a change invalidates your assumptions.
6. Route missing business rules, cross-owner changes, contradictions, and scope
   needs to Master in this record. Continue only independent authorized work.
7. Before submission, run relevant checks and the source scope auditor. Link
   every acceptance criterion to a test or appropriate verification result.
8. Submit an immutable candidate commit and concise handoff. Freeze it for review;
   a correction needs a new task revision and new candidate evidence. Master
   writes task state and verdicts. Do not declare merged/deployed without proof.
   Workspace tasks submit output receipts instead of application commits.
   QA submits report/evidence for the assigned subject instead of a new commit.
   Never move Jira items or interpret technical completion as user acceptance.

Integration specialists additionally read `CONTROL_ROOT/templates/INTEGRATION.md`.
Do not integrate merely because an implementation task has finished.
QA specialists additionally read templates/QA.md and use QA_REPORT.md.

## Session and assignment receipt

- Live session ID / started UTC: <unique ID and timestamp>
- Previous session: <none / explicitly released session and Master handoff reference>
- Session state: <active / checkpointed / released>
- Absolute CONTROL_ROOT / CODE_ROOT: <actual paths>
- Task ID and revision acknowledged: <TASK-ID@revision>
- Jira requirement / approved plan / requirement digest: <KEY@revision, PLAN-ID@revision, hash>
- QA subject digest, when assigned: <exact pinned hash>
- QA report identity, when assigned: <Master-reserved qa_report_ref>
- Policy / charter revisions: <numbers>
- Actual branch / base commit: <verified branch and full SHA>
- Contracts acknowledged: <CON-ID@revision, or none>
- Dependencies checked: <required source revisions and evidence>
- Receipt outcome: <ready to work / blocked with reason>
- Startup Jira check: <UTC / actual scoped references or fresh Master receipt>

## Current work and checkpoint

- Phase / observation: <planning / red / green / refactor / blocked / submitted>
- Smallest plan: <a few steps; omit for trivial work>
- Confirmed source/context: <paths, symbols, commit or approved requirement>
- Unknown/stale context: <gap and effect, or none>
- Last completed step: <specific>
- Current changes / uncommitted work: <paths and state; never discard by assumption>
- Candidate SHA, if submitted: <full SHA>
- Next action: <specific>

## Messages to Master

### MSG-<AGENT-ID>-<number> — <topic>

- Related task/contract and revision: <IDs>
- Type: <question / blocked / boundary change / owner request / navigation update>
- Evidence / current behavior: <source or reproduction>
- Needed decision or change: <exact question / requested owner action>
- Recommendation / impact: <brief>
- Scope paused: <dependent work; independent permitted work may continue>
- Resolution read: <Master decision/task revision reference, or unanswered>

## Boundary acknowledgements

| Contract revision | Role | Outcome | Evidence / unresolved gap |
| --- | --- | --- | --- |
| <CON-ID@revision> | <producer / consumer> | <acknowledged / cannot satisfy yet> | <specific> |

## Verification evidence — current candidate

| Criterion / phase | Command or check | Outcome | Code revision / UTC / evidence |
| --- | --- | --- | --- |
| <AC-1 / red> | <actual command and test> | <expected failure and cause> | <SHA + dirty test diff, timestamp, log reference> |
| <AC-1 / green> | <actual command> | <passed / failed / not run> | <SHA or dirty diff, timestamp, reference> |
| <regression / refactor> | <actual checks> | <actual result> | <revision and reference> |

If new tests are inappropriate for a nonbehavioral change, state the reason and
the replacement check. Behavior-changing TDD exceptions need a Master decision
reference. Summaries without execution are not evidence of passing tests.

## Submission / handoff

- Task revision and immutable candidate SHA: <values>
- Completion target / workspace outputs: <local/promoted; actual setup receipts if applicable>
- QA report, if applicable: <QA-ID@revision, owned path, subject digest, pass/fail/blocked>
- Observable result: <what now works>
- Changed paths / public boundary changes: <brief; full diff is authoritative>
- Acceptance coverage: <AC-ID → evidence; explicit gaps>
- Scope audit / regression / integration checks: <results; distinguish local from combined>
- Environment and reproducibility: <registered profile, fixtures, relevant setup>
- Documentation proposals: <path/symbol/term/contract updates for Master>
- Risks / remaining blockers: <specific, or none>
- Next owner/action: <Master review, source owner correction, or integrator>
- Milestone handoff: <report reference to bring to the sole Master chat; manual or configured runner>
- Session/candidate disposition: <frozen submitted candidate / released session>

## History links

Archive completed evidence under `agents/<AGENT-ID>/archive/` when this record grows.
Keep a short linked receipt per completed task. Never archive another writer's
record or remove current unresolved questions to make the record look complete.
