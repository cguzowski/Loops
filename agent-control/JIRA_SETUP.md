# Jira setup and session-boundary integration

Master maintains confirmed setup facts. A tooling/integration worker implements
the wrapper/timer; the human configures access. This pack installs neither.

## Board and access

1. Configure ordinary statuses/columns in this order: Archive, Backlog, To Do,
   In Progress, Blocked, QA, Done. Only Done uses the Done category; the first
   three use To Do and the middle three use In Progress.
2. Archive remains visible parked work; do not invoke native archiving. Backlog
   is a visible column. Verify the actual epic panel/card view and complete
   child discovery. Activation never automatically approves children.
3. Record actual site URL, project keys, seven distinct status IDs, trusted
   human account IDs and a separate Master identity. Secrets stay outside files.
4. Resolve actual available transition IDs; these differ from status IDs.
   Test read/comment/transitions on a disposable item.
5. Give Master scoped mutation tools; workers/QA get relevant read access only.
   UserAssistant still writes only USER.md.
6. Set jira.enabled only after access/mappings are confirmed. Keep
   integration_status not_installed until the boundary runner is implemented
   and tested. A connector alone does not schedule timeout runs.

## Trigger configuration

- sync_mode: session_boundaries.
- sync_triggers: session_start, milestone, inactivity.
- inactivity_timeout_seconds: 9000 default; allowed range 7200–10800.
- Remove poll_interval_seconds; do not enable periodic polling or Jira webhooks.

Every new/resumed work chat reads relevant Jira at startup. Master reconciles;
other roles read only assigned scope and route findings. During work, local
registry/contract re-reads continue without recurring Jira requests.

An explicit milestone signal in context requests one Jira reconciliation/progress
update. Examples: "this is done", "great work!", "go ahead update Jira".
These signals do not approve a plan or accept a QA report.

For inactivity, arm one deadline after an awaiting-reply checkpoint/summary.
A reply cancels it; after new real user input a later checkpoint may arm another. Explicit milestone sync
consumes it. At 150 minutes of unanswered checkpoint time, inspect actual Jira
and reports once and update verified progress. No response never means acceptance.
After consumption, only new real user input permits another awaiting-reply
checkpoint. The automatic timeout summary cannot rearm itself. Persist session/
project, last user-message ID, checkpoint ID, UTC deadline and consumed IDs;
discard stale callbacks and keep one pending deadline per interaction.

## Bounded implementation handoff

Master proposes a tooling task in the actual versioned source location. Execution
waits for its current human-approved Jira plan and prepared owner/worktree.
Implement the smallest needed wrapper and persistent one-shot deadlines, rather
than a Jira change watcher.

| Component | Responsibility |
| --- | --- |
| Jira adapter | Scoped startup/end reads; controlled owned comment/transition writes |
| Session wrapper | Startup event and explicit user milestone detection in context |
| Local inactivity timer | One deadline/checkpoint, cancellation on reply, one timeout event |
| Queue/outbox | Deduplicate triggers, preserve uncertain writes and restart state |
| Serialized Master runner | Respect sole Master ownership and explicit release/safe handoff |
| Progress reader | Inspect actual worker/QA evidence during the triggered reconciliation |

Runtime metadata belongs to the integration operator, separate from Master/
worker records. Only Master writes plans/snapshots/registry. Fetch current Jira
inside each allowed window, paginate completely, verify genuine approvals and
observe write outcomes. Keep idempotent operation IDs and bounded retries.
The tooling worker edits the assigned source copy; the operator installs its
reviewed executable tooling into CONTROL_ROOT. Do not use CONTROL_ROOT as a
source worktree or duplicate its canonical live records.

Do not fabricate chat-idle monitoring support from Markdown. A real timer needs
a running process and reliable user-message/checkpoint events. If the machine or
runner stops, preserve the deadline and reconcile once on restart/startup.
Do not launch a competing Master or start unapproved implementation on timeout.

## Live acceptance checks

Use a disposable Jira item and controlled local session events:

- Startup reads correct scope once; implementation alone causes no periodic reads.
- Current milestone signal causes one sync; unrelated praise does not.
- Simultaneous signal/deadline/startup events coalesce without duplicate updates.
- Awaiting-reply timeout fires once; a reply cancels it. A later checkpoint after
  new real user input may rearm. A timeout-generated summary cannot rearm it,
  and stale callbacks/sustained silence do not repeat it.
- Running workers remain running; timeout updates only actual observed progress.
- Changes made in Jira during work are handled at the next allowed sync and
  invalidate affected approval/QA rather than silently changing intent.
- Wrong authors, stale approvals and board-only moves cannot approve/accept.
- Passing QA stays QA pending human acceptance; timeout/praise cannot set Done.
- Outage/restart preserves pending writes and avoids duplicate transitions.
- Current complete epic child receipts are verified before rollup QA/Done.

Bundled tests validate local configuration/records, not actual timer delivery
or live Jira. Retain real integration evidence before claiming it running.

## Official references

- [Columns/status mappings](https://support.atlassian.com/jira-software-cloud/docs/configure-columns/)
- [Native archiving](https://support.atlassian.com/jira-software-cloud/docs/archive-an-issue/)
- [Issue APIs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)
- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Non-interactive runs](https://learn.chatgpt.com/docs/non-interactive-mode)

Scoped API calls must respect service limits. Model/hosting costs and CLI access
are separate from Jira plan limits.
