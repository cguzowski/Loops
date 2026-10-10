# Registry fields and issuance rules

Writer: MasterAgent. Schema 2 uses plain JSON and standard-library Python.
The supplied registry is deliberately unconfigured. Values below are illustrative
placeholders; never issue them as actual assignments.

## Top-level fields

| Field | Meaning |
| --- | --- |
| schema_version | 2 |
| revision | Increment for edits; unrelated edits do not cancel every task |
| policy_revision | Current POLICY revision, initially 4 |
| setup_complete | Actual source owners, routes and commands registered |
| protected_source_paths | Governance paths requiring explicit USER decision |
| agents | Sole record writer, charter, source ownership and domain/layer axes |
| contracts | Pinned specification revisions and owner acknowledgement references |
| tasks | Authoritative internal envelopes, not Jira delivery status |
| verification_profiles | Real commands, actual source, disposable environment, safety |
| jira | Confirmed access/mappings/approval identities; no secrets |
| work_items | Local observations, immutable requirement/plan/QA/decision bindings |

Only one Master updates this registry. Use atomic replacement for concurrent
readers; retry incomplete reads rather than assuming an empty registry.

## Jira configuration

Keep enabled false until actual access and mappings are confirmed. Fields:

- site_url: actual HTTPS site, without embedded credentials.
- project_keys: scoped actual projects.
- board_columns: exactly Archive, Backlog, To Do, In Progress, Blocked, QA, Done.
- status_ids: those seven names mapped to seven distinct actual numeric ID strings.
- user_account_ids: trusted human approver account IDs.
- master_account_id: distinct integration account; never a trusted human approver.
- sync_mode: session_boundaries; no poll_interval_seconds field.
- sync_triggers: exactly session_start, milestone, inactivity.
- inactivity_timeout_seconds: 9000 default (150 minutes); allowed 7200–10800.
  One awaiting-reply checkpoint deadline; reply cancels. After consumption,
  rearming requires new real user input; automatic summaries cannot rearm it.
- integration_status: not_installed initially; manual/ready/running only with
  corresponding real setup evidence. enabled does not mean a boundary runner/timer is running.

Status IDs are not transition IDs. Resolve available transitions for the actual
item through Jira. Store secrets outside Markdown/JSON. Read
[JIRA_SETUP.md](JIRA_SETUP.md) before enabling access.

## Work-item entry

delivery covers task/story/bug and similar concrete deliveries. epic is a
container with a reconciled child set, not a single invented source commit.

```json
{
  "<KEY>": {
    "file": "work-items/<KEY>.md",
    "item_type": "delivery",
    "parent_key": null,
    "board_status": "Backlog",
    "requirements_revision": 1,
    "requirements_file": "work-items/<KEY>-r1.json",
    "requirements_digest": "<canonical SHA-256>",
    "plan": null,
    "execution_tasks": [],
    "completion_target": null,
    "candidate_commit": null,
    "target_base_commit": null,
    "qa_task_id": null,
    "final_acceptance": null,
    "promoted_commit": null,
    "promotion_authority": null,
    "resume_status": null
  }
}
```

Use actual Jira keys. Snapshot selected material intent as canonical JSON;
tools/workflow.py digest(value) hashes sorted keys, compact separators and
UTF-8 JSON with ensure_ascii=False. Do not hash unrelated bot/status/processing
changes. Reconcile live Jira before treating a cached snapshot as current.
Keep completion_target null while the outcome is unresolved in Backlog or
Blocked with resume_status Backlog. Approved execution requires local or promoted;
never guess promotion intent. Current execution_tasks contains only tasks bound
to this exact issue request revision/digest and approved plan. Retain superseded
tasks as history/dependencies, not in the current delivery's execution list.

Create plan metadata after interpretation/questions:

```json
{
  "id": "PLAN-0001",
  "revision": 1,
  "file": "plans/PLAN-0001-v1.md",
  "requirements_revision": 1,
  "requirements_digest": "<same snapshot digest>",
  "promotion_authorized": false,
  "approval": null
}
```

The plan file has exact Plan ID and Revision headings. Published revisions are
immutable; edits get a new revision/file. After actual current human approval,
record approval as:

```json
{
  "decision": "approved",
  "author_account_id": "<actual trusted human ID>",
  "source_ref": "jira-comment:<actual numeric comment ID>",
  "plan_ref": "PLAN-0001@1",
  "requirements_digest": "<approved current snapshot digest>"
}
```

Receipt fields do not create authority: fetch the genuine author's comment and
verify its exact command/current bindings. To Do/In Progress/QA/Done require a
current approved plan. Archive never grants execution; Backlog is planning only.
Blocked records resume_status: Backlog, To Do, In Progress or QA.
Clear current QA/acceptance links when invalidated, retaining historical reports
and immutable terminal tasks. Replans/corrections use new tasks where required.

## Agents and ownership

```json
{
  "<owner-id>": {
    "record": "agents/<owner-id>/AGENT.md",
    "charter_revision": 1,
    "specialization": "implementation",
    "domains": ["<actual domain>"],
    "layers": ["<actual layers>"],
    "owns": ["<actual disjoint directory>/"]
  }
}
```

Specializations: implementation, tooling, integration, qa. QA always owns [].
An integration-only agent may own []; exact named source tasks supply its bounded
merge authority. Separate concurrent sessions require separate IDs/records.

Scopes are exact repo-relative files or prefixes ending in /. No globs, absolute
paths, repository-wide grants or overlapping owners. Case-only overlaps are
rejected conservatively for portability; audit authorization is case-exact.
Domains/layers route context; they never create overlapping write permissions.

## Execution task envelope

```json
{
  "TASK-0001": {
    "revision": 1,
    "policy_revision": 4,
    "charter_revision": 1,
    "request_ref": "<KEY>@1",
    "plan_ref": "PLAN-0001@1",
    "requirements_digest": "<same current snapshot digest>",
    "kind": "implementation",
    "completion_target": "local",
    "assignee": "<owner-id>",
    "file": "tasks/TASK-0001.md",
    "state": "draft",
    "base_commit": "<full actual Git SHA>",
    "branch": "<prepared unique branch>",
    "worktree": "<absolute prepared worktree>",
    "write_paths": ["<owned assigned path>/"],
    "contracts": [],
    "depends_on": [],
    "verification_profiles": ["<actual profile>"],
    "candidate_commit": null,
    "completion_evidence": null,
    "promoted_commit": null,
    "merge_sources": [],
    "governance_approval": null,
    "promotion_authority": null
  }
}
```

The linked Markdown has matching Task ID and Revision. Issued work has real
SHA/roots, profiles, approved bindings and reserved owner-covered paths.
execution_tasks on its source item names all authorized technical tasks.
QA is listed separately as qa_task_id.

States: draft, ready, running, blocked, review, verified, integrating, done,
cancelled. Master writes state; workers write observations. Nonterminal issued
tasks retain reservations. Blocked is paused, not released. One live task/session
per agent record; worktree/branch reservations must also be unique.
Paused tasks keep original issuance bindings without write authority. Revalidate
and reissue current policy/charter/request/contracts before acknowledgement and
resume; they must not prevent independent current assignments. Windows worktree
paths differing only in case/slashes count as the same reservation.

USER RQ references remain for bootstrap/global records and terminal history;
they cannot bypass approved Jira execution. Protected source changes additionally
require governance_approval naming an actual USER DEC decision.

Dependencies use {"task_id":"TASK-0000","required_state":"done"} or a required
verified milestone. Inspect exact candidate ancestry in the dependent worktree:
local done does not place code in another checkout. Reject cycles and stale
dependencies. Pin contract revisions and require matching owner acknowledgements.

Technical local tasks can complete at a verified candidate/setup/report milestone,
while Jira remains QA. Promoted tasks require explicit authority and observed
promotion. Every done task has completion_evidence. Terminal envelopes/source
receipts remain immutable; follow-up gets a new task ID.
Preserve historical promotion source references when an item is replanned or
reopened. Such retained receipts do not grant new execution/promotion authority.

## Independent QA binding

Create a qa-specialized agent with no ownership. It must differ from every linked
execution assignee. A qa task has completion_target local, write_paths [],
merge_sources [], safe verification profiles and exact current request/plan/digest.
Before issuance, Master sets `qa_report_ref`, for example `QA-0001@1`, unique
across all QA tasks including history. QA uses that reserved ID/revision. A new
report revision uses a new file; reissue a nonterminal task with acknowledgement,
or create a new task after terminal completion. Never overwrite a submitted report.

Compute qa_subject using workflow.subject_for(key, item, registry), and
qa_subject_digest using workflow.digest(subject). A delivery subject contains
kind candidate, issue_key, requirements_digest, plan_ref, completion_target,
candidate_commit and, for promoted delivery, target_base_commit. Both SHAs
must be exact full actual commits. Pin task.base_commit to the candidate and use
a prepared isolated checkout. A QA audit rejects source changes and a different HEAD.

When QA submits, Master records its owned report receipt without editing it:

```json
{
  "id": "QA-0001",
  "revision": 1,
  "file": "agents/<qa-agent-id>/archive/QA-0001-v1.md",
  "verdict": "pass",
  "subject_digest": "<exact qa_subject_digest>"
}
```

The report has Report ID and Revision headings. Verdict is pass/fail/blocked.
Report-task done means the report was delivered/reviewed, including a failing
report; it does not mean accepted delivery.

Final acceptance is recorded only from the actual human comment:

```json
{
  "decision": "accepted",
  "author_account_id": "<actual trusted human ID>",
  "source_ref": "jira-comment:<actual numeric comment ID>",
  "plan_ref": "PLAN-0001@1",
  "requirements_digest": "<current approved digest>",
  "qa_report_ref": "QA-0001@1",
  "subject_digest": "<current exact QA subject digest>"
}
```

QA pass stays QA until this genuine current acceptance. Before Jira Done,
the QA report task and linked execution tasks must be done with evidence.
Promoted delivery additionally records promoted_commit equal to candidate_commit
and explicit user-derived promotion_authority. Authority may reference the
current plan-approval comment only when the approved plan expressly grants that
promotion (promotion_authorized true). A standalone acceptance comment grants
no publication/deployment authority.

## Epics

Use item_type epic and child_keys naming the freshly fetched complete scope.
Each registered child's parent_key agrees with that set. Before epic QA/Done,
all children are accepted Done. The subject contains sorted children with
issue_key, acceptance_ref and subject_digest from each genuine current child
acceptance. It omits candidate_commit. QA rolls up outcome/integration evidence;
the user accepts the exact report/child subject. Reopened or changed children
invalidate it. Local registry checks cannot prove Jira pagination was complete;
Master must inspect live hierarchy.

## Contracts and profiles

Contract keys such as CON-0001@1 map to file, state (draft/agreed), producer,
consumer and acknowledgements. agreed needs both owners' references to their own
matching revision receipts. Publish changes as new files/revisions, then reissue
affected assignments; never edit a pinned specification silently.

Profiles contain commands (actual nonempty command descriptions), source (real
script/manifest at SHA, or verified installed tool/version and source base),
environment (disposable fixtures/output) and master_safe.
True means checked for no source/snapshot/production changes. Master and QA use
only safe profiles. Unsafe setup/source changes require a source-owner task.
The validator stores descriptions; it never executes them.

## Integration and workspace kinds

Integration requires an integration specialist, write_paths [] and merge_sources:

```json
[
  {"task_id": "TASK-0001", "commit": "<exact verified source SHA>"},
  {"task_id": "TASK-0002", "commit": "<exact verified source SHA>"}
]
```

Effective merge scope is only their historical union. Sources freeze; one
integration task holds each source. This bounded handoff is the sole permitted
reservation overlap. Completed scopes must be reacquired without colliding with
current work. Integration cannot implement semantic fixes privately.
Create/freeze the combined candidate before independent QA. Promote only after
passing current QA, human acceptance, explicit authority and unchanged target base.

Workspace tasks use an integration specialist, kind workspace, completion_target
local, write_paths [], merge_sources [] and workspace_outputs with exact branch,
absolute worktree and base_commit for each output. The assigned operator checkout
already exists. Create only declared outputs, preserving collisions; no source
edits, merge, deletion/reset or promotion. Master observes roots/branches/SHAs/
clean status and records completion_evidence; no application commit is required.

## Issuance and migration

Run check --ready after confirmed setup and before issuing ready work.
Validate scope, dependencies, contracts, approved bindings and session/worktree
uniqueness. Do not treat boundary-runner integration_status as installed without live tests.

For 1.0 → 1.1, retain existing owned records and terminal history. Checkpoint
affected work, add schema-2 Jira/work-item/QA fields, verify actual mappings and
rebind active execution to newly approved current plans. Never backfill fictional
human approvals. See START_HERE's upgrade instructions.

For 1.1 → 1.2, remove polling configuration, disable periodic/webhook Jira wake-ups,
and use the three boundary triggers with a one-shot 150-minute local deadline.
Re-acknowledge affected active policy receipts; terminal evidence stays immutable.
Runtime last-user-message/checkpoint/deadline/processed IDs belong to the
integration operator, not a second writer of this registry.
For 1.2 → 1.2.1, preserve the pre-migration registry. Add qa_report_ref to existing
QA entries only from their actual frozen report, documenting this as additive
migration metadata rather than proof of an earlier reservation. Keep the original
report, task state, candidate and authority receipts unchanged. Unsubmitted QA
needs a real reserved identity/reissue and current policy acknowledgement before
resume. Never invent missing historical evidence.
