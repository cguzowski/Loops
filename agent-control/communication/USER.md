# User direction and communication

Writer: User / the user's separate UserAssistant session only.
Revision: 4

## Standing direction

- Build a maintainable SaaS using stack-neutral agent governance.
- MasterAgent is technical PM and quality coordinator: plan, delegate, define
  boundaries, review and safely verify; never edit executable source or source Git.
- Workers own real product domains and technical layers. Every source path has
  one writer; workers report to Master.
- Use TDD for behavior changes/bugs and keep implementation clear and lean.
- My personal Codex edits only this file. Master owns MASTER.md. Neither writer
  edits the other's file; I do not maintain worker records.
- Jira is the product request/approval/progress source. Board order is Archive,
  Backlog, To Do, In Progress, Blocked, QA, Done.
- Archive holds my parked epics/tasks/ideas. I activate them; agents leave them parked.
- Master first explains changed intent and proposes a plan. Implementation waits
  for my explicit approval of its current plan revision.
- Check Jira at chat startup and clear milestone/end only, with one fallback
  after an awaiting-reply checkpoint has no response for 2½ hours. No recurring
  polling. Progress signals/inactivity do not supply plan approval or acceptance.
  A consumed timeout cannot rearm itself during the same user silence.
- A separate QA agent tests the result and owns its report. I make the final
  acceptance decision; QA pass alone does not authorize Done.

## Product brief

- Product / intended users: <unknown until supplied>
- Problem and desired outcomes: <describe>
- Existing source repository / canonical checkout: <absolute actual path>
- Established stack: <confirmed facts, or undecided>
- Current priority: <describe; per-item priority lives in Jira>
- Business rules / constraints: <actual requirements; do not infer>
- Jira site/project/board: <actual identifiers; no secrets>
- Source promotion: Explicit standing or task-specific authority required.
  Local candidate creation under approved tasks is permitted.
  Remote publication/deployment is not granted here.

## Bootstrap and global requests

### RQ-0001 — Bootstrap the development protocol and Jira workflow

- Revision: 2
- Outcome: Master inspects the actual project read-only; proposes minimal
  domain/layer ownership and independent QA; creates initial records/navigation;
  confirms real verification profiles and Jira setup gaps.
- Acceptance: No guessed facts; one source owner/path; separate QA report owner;
  two owned communication files; correct board/approval rules; structural checks
  pass and readiness accurately reports unresolved setup.
- Scope: Documentation/intake/read-only discovery. Application implementation,
  boundary-runner/timer code and global Jira configuration require concrete approved setup plans.
  No stack choice, source promotion, remote publishing or deployment granted.
- Priority: First.

### RQ-<ID> — <bootstrap/global outcome>

- Revision: <increase when intent changes>
- Outcome / acceptance / constraints: <specific>
- Effective scope: <affected policy, setup or global facts>
- Authority / exclusions: <explicit>

Create product work in Jira, not as a duplicate editable request here.

## Answers to Master

### Answer to Q-<ID>, about <request/issue revision>

- Answer: <specific>
- Decision ID if changing an enduring rule: DEC-<ID>
- Effective scope / supersedes: <specific references>

Answer per-item plan/QA questions in Jira. Record enduring direction here.

## User decisions

### DEC-0001 — Adopt Jira planning and independent QA

- Decision: Use the seven-column order and current-plan approval before execution.
  Independent QA reports results; my acceptance is required before Done.
- Authority: User's request to update this uploaded foundation to that workflow.
- Effective scope: Policy revision 2; schema version 2; version 1.1 templates.
- Limits: No future product-plan approval, final QA acceptance, source promotion,
  deployment or external account change is implied.
- Supersedes: Version 1.0's USER-only product intake and Master-only delivery completion.

### DEC-0002 — Synchronize Jira at session boundaries

- Decision: Read Jira at startup and a clear user milestone/end signal; reconcile
  once after 2–3 hours without a checkpoint reply, default 150 minutes.
- Authority: User's request to replace recurring checks with this workflow.
- Effective scope: Policy revision 3 / version 1.2; approval/QA rules unchanged.
- Supersedes: Version 1.1 recurring polling/webhook wake-ups only.
- Limits: No inactivity timer or external account setup installed by this edit.

### DEC-0003 — Review and clarify foundation readiness

- Decision: Preserve the established workflow; resolve confirmed ambiguity and
  guard gaps in bootstrap, manual handoffs, paused work and evidence identity.
- Authority: User's request for a thorough review and improvements only where needed.
- Effective scope: Policy revision 4 / version 1.2.1; existing approval/QA gates,
  role ownership, board order and TDD direction remain in force.
- Limits: No product stack choice, future execution approval, external account
  configuration or installed runtime is implied.

### DEC-<next ID> — <enduring decision>

- Decision / authority and limits: <specific>
- Reason / effective scope / supersedes: <specific>

## Writing rules for my UserAssistant

Read Master's relevant questions/results but edit only this file. Preserve
standing decisions, increment applicable revisions and express my actual intent.
Do not fabricate approvals, answered questions, facts or completion.
The human uses Jira directly for APPROVE PLAN-<ID>@<revision> and
ACCEPT QA-<ID>@<revision>. This personal session does not write Jira or other files.
