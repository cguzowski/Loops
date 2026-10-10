# Jira development workflow

Policy revision: 4. Maintainer: MasterAgent under the user's direction.
Jira holds product requests, board status, plan approvals, and final acceptance.
Markdown holds operating rules, navigation, assignments, and evidence. Jira
snapshots are receipts, never a competing requirements editor.

## Board order and meaning

Keep these seven columns in this exact left-to-right order. Blocked is a branch,
not a mandatory stop for every task.

| Column | Jira status category | Meaning / entry condition | Responsible actor |
| --- | --- | --- | --- |
| Archive | To Do | User's parked epics, tasks, stories, bugs, and ideas. No automatic planning or execution. | User alone parks/activates |
| Backlog | To Do | Activated request; Master clarifies, inspects context, and proposes a plan. Approval pending. | User supplies intent; Master proposes |
| To Do | To Do | Current plan explicitly approved; queued for prepared workspaces and available owners. | Master records genuine user approval |
| In Progress | In Progress | Approved execution started; worker acknowledged its bounded assignment. | Master coordinates; owners implement |
| Blocked | In Progress | A dependency, clarification, changed requirement, or environment prevents the next step. | Master records cause, owner, and previous stage |
| QA | In Progress | Frozen delivery is independently tested or awaiting the user's final decision. | QA agent reports; user accepts/requests changes |
| Done | Done | Current passing QA, explicit final user acceptance, and agreed local/promoted delivery evidence exist. | Master observes gates and updates Jira |

Archive is an ordinary custom status. Jira native archiving removes items from
active views. Backlog here is a visible board column, not only a separate backlog
panel. Done alone belongs to the Done category and rightmost completion column.

## Ownership and authority

- User owns request text, acceptance intent, business priority, Archive activation,
  plan decisions, and final QA decisions.
- Master owns its plan/status/report comments and permitted progress updates.
  Preserve user text; never fabricate or post as the user to satisfy approval.
- Workers own records and assigned source. They do not move Jira items or edit
  requirements. Logical worker IDs do not require separate Jira seats.
- QA owns its record, report, and evidence. It does not implement fixes, edit
  source, approve its own report, or set the user-facing issue Done.
- The tooling/integration operator owns boundary-runner code and runtime state. Master
  alone owns coordination Markdown/registry. The boundary runner queues startup/milestone/timeout events for a
  serialized Master run rather than editing Master/worker records itself.

Keep the two owned communication files. USER retains global direction, bootstrap
facts, and enduring decisions. Per-item discussion/approval happens in Jira.
UserAssistant still edits only USER.md. Do not copy Jira descriptions into USER
as a second editable backlog.

## Intake and understanding

When an allowed synchronization detects Backlog activation or a material active
request change, Master fetches
current Jira data and relevant linked work. It states the understood outcome,
specific delta, acceptance examples, constraints, assumptions, and questions;
identifies actual affected code/owners/contracts/dependencies; then proposes a
plan and the exact decision needed. Unknown business meaning stays unknown.
Backlog work is inspection and planning only. Use [PLAN.md](templates/PLAN.md)
and [JIRA_ITEM.md](templates/JIRA_ITEM.md).

Retain immutable selected requirement snapshots in
`work-items/<KEY>-r<n>.json`. Canonicalize JSON with `tools/workflow.py`'s
`digest()` function. Include summary, description/acceptance fields, constraints,
completion target, relevant links, parent/child membership, and human clarification
that changes intent. Preserve rich-text structure and actual values. Exclude bot
comments, processing times, QA results, and status-only changes from this digest.
Jira updated time discovers changes; it does not identify an approved requirement.

## Approval before execution

Publish an immutable plan ID/revision tied to the selected request revision/digest,
owners/tasks, checks, and completion target. Example human Jira comment:

```text
APPROVE PLAN-0001@2
```

Read the actual comment, authenticated author account, and current plan/request.
Only a configured human account can approve. Record its comment ID and exact
bindings, then move to To Do. A drag, assignment, label, emoji, or bot comment
alone is not approval. Suggestions cause a revised proposal and do not authorize
unapproved scope. One approved plan can authorize several named internal tasks.

Master may draft assignments in Backlog but issues execution only after approval,
readiness, dependencies, and reservations. Prepare branches/worktrees through a
bounded workspace task or human operator. Separate worker chats remain manually
started unless an integration explicitly implements a worker launcher.

## Change, pause, and resume

Material requirement changes invalidate dependent plan approval, QA, and final
acceptance. Before execution, return to Backlog for a new plan. During In Progress
or QA, stop affected work, checkpoint it, and use Blocked while reconciling impact
and a new plan. Preserve independent authorized work. Priority-only changes can
reorder the queue without rewriting an unchanged plan.

Store `resume_status`. Resume after blocker resolution, current approval, and
owner acknowledgement. Behavioral QA failures normally route a bounded fix back
to In Progress; missing access/fixtures/dependencies may require Blocked. Re-run
affected QA with a new report revision. Never reuse an old pass for changed code.

Keep paused tasks' original issuance receipts and reservations until a confirmed
release/reissue. Stale bindings on a blocked task are history, not write authority;
they do not stop independent currently authorized tasks. Clear invalid current
plan/QA/acceptance links while retaining their immutable history. Revalidate the
affected envelope and obtain current owner acknowledgement before resuming.

If the user parks active work in Archive, request stop/checkpoint receipts and
preserve changes. No execution is allowed there. Release reservations only after
stop/cancellation/handoff is confirmed; time alone does not release a session.
Agents never automatically activate Archive ideas or their parked children.

## Independent QA and final decision

Master reviews worker evidence and prepares a frozen delivery candidate. For
cross-owner work, IntegrationAgent combines exact reviewed commits before QA.
Master defines boundary expectations; QA independently verifies real outcomes
using [QA.md](templates/QA.md) and [QA_REPORT.md](templates/QA_REPORT.md).
Before issuing QA, Master reserves its exact unique `qa_report_ref` globally.
QA uses that assigned identity/revision; submitted revisions remain immutable.
New report revisions get new files and bindings; terminal QA tasks require a
new task ID. Agent IDs and report IDs are separate identifiers.

QA checks acceptance, affected regressions, real interfaces, and applicable
failure/access/isolation cases. It reports executed checks, results, exact subject
and environment, reproducible defects, and untested gaps with pass/fail/blocked.
QA owns the report. Master reviews its evidence and posts a summary/link in Jira.

The user inspects the result and current report. Example final comment:

```text
ACCEPT QA-0001@2
```

Acceptance binds the report, request digest, plan, and exact candidate/child
receipts. A normal comment can request changes. A manual drag to Done alone is
not acceptance. If a move bypasses a gate, report the discrepancy; do not mark
local records accepted or silently rewrite user requirements/status.

A pass stays QA until user acceptance. Fail/blocked/skipped mandatory checks
cannot satisfy Done. Replacing the report, request, plan, or candidate invalidates
final acceptance; the current report needs a new human decision.

For local completion, pass plus acceptance permits Done without promotion. For
promoted completion, explicit source-promotion authority is also required. After
acceptance, the integrator promotes the exact tested candidate if the target base
is still current; Master observes it before Done. A changed target requires a
rebuilt candidate and renewed relevant QA/acceptance. Done never grants deployment.

## Epics and internal tasks

Epics group outcomes, not blanket implementation authority. Master proposes
decomposition and scoped plans; parked children remain Archive until the user
activates them. Epics may appear in a panel/list rather than normal cards depending
on board type; verify the actual view and maintain explicit workflow statuses.

Before epic QA/Done, fetch the complete current scoped child set. All children
must be accepted Done. QA issues a rollup report of the epic outcome/integration
gaps and exact child acceptance receipts; the user accepts it. The epic subject
is a digest of child receipts, not a fabricated single code SHA. New/reopened/
changed children invalidate the rollup and acceptance.

Jira stages are user-visible delivery. Internal TASK states are technical
assignments. A workspace/candidate/report task can be done while Jira remains QA.
A QA task done means its report was produced/reviewed, even if the report says
fail; it never means user acceptance. Before Jira Done, Master closes the linked
execution assignments with their verified milestone evidence.

## Session start, milestone and inactivity synchronization

Check Jira only in these synchronization windows. No recurring Jira poller and
no Jira-change webhook automatically wakes Master.

| Trigger | Action |
| --- | --- |
| New or resumed chat | Read relevant scoped Jira once before execution. Master reconciles changes/decisions; workers/QA read only their assigned items. Disabled Jira permits authorized documentation/read-only bootstrap only. |
| Explicit milestone/end | In context, "this is done", "great work!", "go ahead update Jira" or equivalent requests one reconciliation and permitted progress writeback. A milestone need not close the chat. |
| No user reply for 2½ hours | One reconciliation/writeback for the pending checkpoint; never repeated polling during the same silence. |

Arm the inactivity deadline when an agent posts an implementation/checkpoint
summary or question and is awaiting the user's reply. Default 9000 seconds
(150 minutes); configurable within 7200–10800 seconds. Any user reply cancels
the old deadline. A later awaiting-reply checkpoint may arm a new one after real
user input. Timeout or explicit milestone consumes that interaction's checkpoint;
automatic summaries, worker reports and new timestamps cannot rearm during the
same silence. A new real user message/user-started session permits a later checkpoint.
Before consumption, a newer checkpoint may replace the single pending deadline.
Coalesce simultaneous startup/milestone/timeout triggers. Persist session/project,
last user-message ID, checkpoint ID, UTC deadline and consumed/processed IDs in
operator-owned runtime state. Discard callbacks superseded by a reply.

The timer watches local session activity, not Jira changes. It does not assume
waiting workers finished, terminate them, release reservations, approve plans,
accept QA, promote source or mark Done. Inspect actual owned reports/candidates
and update only confirmed progress. Praise about unrelated work is not a trigger.

Master alone writes Jira and coordination data. Other roles perform their
startup read, maintain owned records and route milestone/progress requests to
Master. UserAssistant still writes only USER.md. A boundary runner queues one
serialized Master reconciliation and cannot take over an active Master by time
alone. A timeout during an active run waits for a safe handoff.

For manual chats, the user brings worker/QA report references back to the sole
Master chat with a milestone signal. A report file does not wake Master. If a
worker lacks Jira read access, Master must supply a fresh scoped startup receipt
for this launch: UTC, issue key, current requirement digest and approved plan.
Without that receipt, stop dependent writes; never treat an old cache as current.
Startup scope is known active/assigned keys and activated Backlog intake, including
known active keys newly parked in Archive. Do not load every parked idea/history.

During implementation use live local assignment/contract checks at phase
boundaries; do not add Jira network reads each phase. Jira edits between sync
windows are discovered at the next allowed check. Then assess intent changes,
checkpoint affected work and replan; never silently apply old approval to new intent.

Inside each synchronization window, fetch current scoped issues, relevant
comments, hierarchy and worker evidence. Deduplicate/coalesce triggers and
events since the last receipt, use full pagination, and authenticate decision
authors. Re-read current bindings immediately before permitted writes/dispatch.
Identify self-originated operations without losing interleaved human edits.

Use actual available transitions/status IDs, preserve user fields and post
idempotent plan/blocker/QA/completion comments. Bounded retries may finish the
current window; on outage or uncertain write, retain pending operations and
reconcile them at the next allowed trigger. Do not claim success without observing
Jira. Cached receipts or elapsed time never invent approval/acceptance.

A Markdown rule cannot wake an idle CLI process. A running local/hosted one-shot
timer and session wrapper must deliver the timeout event; see JIRA_SETUP.md.
Without that integration, start/milestone checks require active turns and a
missed timeout is reconciled at the next startup or manual milestone. No board, connection, timer,
boundary runner or launcher is installed by this pack.
