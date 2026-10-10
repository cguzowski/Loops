# SaaS agent foundation

Version 1.2.1 — reviewed Jira workflow with independent QA and final user acceptance.

You direct the product in Jira. MasterAgent interprets changes, proposes plans,
delegates approved work, reviews evidence and updates progress. Domain/layer
owners implement; IntegrationAgent combines source changes; QAAgent tests the
frozen result and reports. You make the final acceptance decision.

## Your board

| Column, in order | Purpose |
| --- | --- |
| Archive | Your parked epics/tasks/ideas. You activate them; agents do no work here. |
| Backlog | Master clarifies intent and proposes a plan for your decision. |
| To Do | Current plan approved; work queued for owners and prepared workspaces. |
| In Progress | Approved work underway. |
| Blocked | Reason, responsible owner and return stage recorded. |
| QA | Independent QA report, then your final decision. A pass remains here. |
| Done | Passing current QA, your acceptance and agreed delivery evidence confirmed. |

Archive is a normal visible status, not Jira's native archive operation.
Backlog is a visible column. Blocked is an exception path, not a required stop.
See [JIRA_WORKFLOW.md](agent-control/JIRA_WORKFLOW.md) for exact rules.

Master publishes a plan ID/revision. Approve in Jira with a comment such as:

```text
APPROVE PLAN-0001@2
```

Suggestions produce a revised plan. After QA, accept the current report with:

```text
ACCEPT QA-0001@2
```

Only configured human accounts can make these decisions. Card movement alone
does not approve a plan or accept a delivery. Changed requirements invalidate
affected approvals; changed code/report requires current QA and renewed acceptance.
Failed QA returns a bounded fix to its source owner.

For a local deliverable, accepted QA permits Done without source promotion.
For a promoted deliverable, explicitly authorized promotion of the exact tested
candidate must also be observed. Deployment needs separate authority.

## Install the shared foundation

Keep agent-control/ in one stable location OUTSIDE all source worktrees:

| Example location | Purpose |
| --- | --- |
| C:/dev/my-saas/agent-control | Canonical live records and navigation |
| C:/dev/my-saas/code | Source repository / shared target |
| C:/dev/my-saas/worktrees/<task> | Isolated task branch/worktree |

Every local chat reads the same control folder. Back it up/version it separately;
feature branches must not carry editable copies. Different machines need a shared
service that preserves one writer and current reads.

The setup owner installs AGENTS.md at the source root, merging existing
instructions carefully, then commits that bootstrap before feature worktrees.
For a new repository, the human/setup operator initializes Git and makes this
first commit. Your UserAssistant remains USER-only; Master does not perform Git setup.
Use [LAUNCH_PROMPTS.md](agent-control/LAUNCH_PROMPTS.md) with real absolute paths.
No CLI profile, board, boundary runner or launcher is installed by this package.

## Keep your two communication files

The communication directory still contains exactly two Markdown files:

| File | Sole writer | Purpose |
| --- | --- | --- |
| [USER.md](agent-control/communication/USER.md) | You / your personal UserAssistant | Standing direction, product facts, enduring decisions, bootstrap answers |
| [MASTER.md](agent-control/communication/MASTER.md) | Master | Operating record, interpretation, questions, routing and verdicts |

Product requests, per-item approvals and final decisions live in Jira.
Your personal Codex edits only USER.md; Master never edits it. Master creates
each worker's record once; that worker then owns it. QA owns its reports.
Do not maintain a second editable backlog in USER.md or the registry.

## Bootstrap and connect Jira

1. Confirm Python 3.10+, Git and your installed/authenticated Codex CLI. Install
   the shared folder and source entry point as above. Fill actual repository/product
   facts in USER.md. Unknowns may remain unknown.
2. Launch one Master with the explicit prompt. It inspects source read-only, proposes the smallest real
   domain/layer map, identifies verification commands and registers owners.
3. Register an independent QA specialist with no source write ownership.
4. Follow [JIRA_SETUP.md](agent-control/JIRA_SETUP.md): configure all seven statuses,
   actual mappings, trusted human account IDs and scoped integration access.
5. Verify a disposable item's transitions, approval identity and write receipts.
   Set jira.enabled only after access is confirmed; complete source bootstrap.
6. Run the read-only readiness check before issuing any execution assignment.

The starter is intentionally unconfigured: no application stack, owners, commands,
Jira account IDs or secrets are invented. Structural checks pass; readiness fails
until setup is complete.

You can begin the authorized documentation/read-only bootstrap while Jira is
disabled or unavailable. Master records gaps and prepares navigation/owned records;
it cannot issue product or tooling implementation without confirmed Jira access,
readiness and a current approved plan. For an empty application, first register
verified source-preserving Git checks for an approved scaffold/test-harness task.
Its owner implements the harness; Master then registers the actual application
checks before issuing feature behavior work. Do not invent test commands.

Run the starter's structural check now (substitute the actual path):

```text
python <CONTROL_ROOT>/tools/validate.py check --control-root <CONTROL_ROOT>
```

Use `python3` or `py -3` where appropriate. Add `--ready` after setup; the starter
is expected to report missing readiness rather than pretend it is configured.

## Concurrent work and QA

Master snapshots understood requirements, publishes a versioned plan and waits
for your approval. It reserves disjoint source scopes and issues bounded tasks.
A human/operator or IntegrationAgent prepares worktrees; Master verifies setup
without performing source Git mutations.

You can open separate CLI chats for each task. Each has a distinct agent ID,
record, session ID and worktree. Paste its explicit launch prompt; a plan does
not start a worker chat. Workers acknowledge revisions, use TDD and submit frozen
commits with actual evidence. Cross-owner changes require agreed contracts.

Master reviews exact commits and delegates combined-candidate creation where
needed. QA tests that frozen subject in an isolated environment, writes its
report, and routes defects back to the responsible owner through Master.
Master publishes the report in Jira and waits for your final decision.

Internal TASK completion describes a technical milestone, such as producing
a candidate or QA report. It does not set the Jira delivery Done.
Keep terminal task receipts immutable; corrections get new task IDs.

### One manual delivery cycle

1. In Jira, activate an item from Archive to Backlog. Start/resume the sole Master
   chat; Master explains the request and publishes `PLAN-…@revision`.
2. Comment `APPROVE PLAN-…@revision` in Jira. Return to Master with a milestone
   signal to reconcile that decision and issue prepared assignments.
3. Start each worker chat with its exact prompt. Workers write owned receipts and
   frozen evidence. When ready, return to Master: "Go ahead update Jira for
   <KEY>; inspect <TASK-ID> and its worker report." A worker's report alone does
   not notify an idle Master; carry this handoff yourself unless a runner is installed.
4. Master reviews the candidate, reserves a QA report ID/revision and issues the
   QA task. Start the separate QA chat with its prompt; return its report reference
   to Master for review and publication in Jira.
5. Inspect the exact report/result. Comment `ACCEPT QA-…@revision` in Jira or
   request changes, then signal Master to reconcile. Master confirms all delivery
   gates before Done; any required promotion stays separately authorized.

Workers without Jira read access need Master's startup reconciliation for this
launch, containing UTC, issue key, current requirement digest and approved plan.
An old cached receipt is insufficient. Missing current evidence blocks writes.

## When Jira is checked

Each new/resumed work chat reads relevant Jira at startup. Master reconciles
changes; workers/QA read only assigned scope. During implementation there is
no recurring Jira polling.

At a clear milestone, say "this is done", "great work!", "go ahead update Jira"
or equivalent. Master checks current Jira and actual reports, then updates
confirmed progress. This is a checkpoint; you need not close the chat.

If an implementation/checkpoint summary awaits your reply for 2½ hours
(150 minutes), reconcile once. A reply cancels that deadline; a later checkpoint
can rearm it only after new real user input. An automatic timeout summary cannot
rearm itself during the same silence. Inactivity never
proves work finished or supplies plan approval/final QA acceptance.

The inactivity fallback needs a running local/hosted one-shot timer and session
wrapper. Markdown alone cannot wake an idle CLI. Without the configured runner,
missed timeout checks happen on the next startup or manual milestone. See
[JIRA_SETUP.md](agent-control/JIRA_SETUP.md) for setup and live acceptance checks.
The bundled tools are read-only guards, not a Jira connection or installed timer.

## Templates and checks

| File | Use |
| --- | --- |
| [POLICY.md](agent-control/POLICY.md) | Ownership, concurrency, TDD and evidence rules |
| [INDEX.md](agent-control/INDEX.md) | Find relevant owner/context without loading every record |
| [PLAN.md](agent-control/templates/PLAN.md) | Interpretation, proposed work and your approval |
| [JIRA_ITEM.md](agent-control/templates/JIRA_ITEM.md) | Current intake and synchronization receipts |
| [SUBAGENT.md](agent-control/templates/SUBAGENT.md) | Every worker's owned operating record |
| [TASK.md](agent-control/templates/TASK.md) | Bounded assignment and acceptance criteria |
| [CONTRACT.md](agent-control/templates/CONTRACT.md) | Producer/consumer boundary agreement |
| [QA.md](agent-control/templates/QA.md) / [QA_REPORT.md](agent-control/templates/QA_REPORT.md) | Independent QA procedure and report |
| [INTEGRATION.md](agent-control/templates/INTEGRATION.md) | Worktree setup, combination and gated promotion |
| [REGISTRY_GUIDE.md](agent-control/REGISTRY_GUIDE.md) | Schema 2 fields and issuance rules |
| [tools/README.md](agent-control/tools/README.md) | Structural/workflow/scope checks |
| [VALIDATION.md](VALIDATION.md) | What was actually checked and remaining limits |

The stable foundation is the authority/ownership/evidence protocol. Update factual
indexes as the product changes. Narrow verified context, real checks and explicit
handoffs reduce errors; templates alone cannot guarantee correctness or enforce
filesystem permissions.

## Upgrading an existing installation

Policy revision 4 clarifies bootstrap, handoffs and evidence bindings. Preserve filled USER/MASTER/worker
records; migrate their procedures rather than replacing their content blindly.
Checkpoint affected live sessions, add schema-2 Jira/work-item fields and QA
ownership, then rebind active work to current explicitly approved Jira plans.
Do not invent retroactive approvals or rewrite terminal task evidence.
For 1.1 → 1.2, replace polling configuration with the three sync triggers and
150-minute timeout; disable old polling/webhook wake-ups and migrate affected
active task policy receipts. Preserve all prior human approvals and terminal history.
Restart chats when their automatically loaded AGENTS instruction chain changes.
For 1.2 → 1.2.1, reserve `qa_report_ref` before QA issuance, retain paused/history
receipts and adopt the clarified one-time timeout rule. Revalidate affected live
tasks and acknowledge the current policy before resuming; preserve prior authority.

## Official references

- [Codex AGENTS discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex CLI flags](https://learn.chatgpt.com/docs/cli/reference)
- [Git worktrees](https://git-scm.com/docs/git-worktree)
- Jira integration references are in [JIRA_SETUP.md](agent-control/JIRA_SETUP.md).

These sources describe tool behavior. This pack defines the proposed project
protocol; it does not configure external accounts.
