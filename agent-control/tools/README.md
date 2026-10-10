# Read-only validation

Requires Python 3.10+ and Git for source auditing; no Python packages.
Use python3 or py -3 if needed. No network calls or record/Git writes.

## Structure and readiness

```text
python <CONTROL_ROOT>/tools/validate.py check --control-root <CONTROL_ROOT>
python <CONTROL_ROOT>/tools/validate.py check --control-root <CONTROL_ROOT> --ready
```

The first accepts a structurally valid unconfigured starter. Ready requires
actual owners/profiles, an independent QA specialist, completed bootstrap and
confirmed Jira configuration. A manual integration may be ready without a timer;
the inactivity fallback then waits for a running wrapper or the next manual sync.

Checks cover schema/policy/record revisions, ownership/reservation collisions,
agent/branch/worktree uniqueness, dependencies/contracts, frozen integration
sources, workspace-output grants and local/promoted milestone receipts.

workflow.py checks session-boundary mode, the three triggers and a 2–3-hour
inactivity timeout; it also adds exact column order, current approved plan/request snapshots,
trusted-author receipt fields, no Archive/Backlog execution, independent source-free
QA, exact subject/report bindings, final acceptance, observed-promotion fields
and epic child rollups. USER requests cannot bypass Jira execution approval.
QA report revisions must match Master's unique reserved qa_report_ref. Paused
tasks retain historical bindings/reservations without blocking independent valid
work. Current delivery completion cannot borrow tasks from another request.

## Narrow context query

```text
python <CONTROL_ROOT>/tools/validate.py show --control-root <CONTROL_ROOT> --agent <AGENT-ID> --task <TASK-ID>
```

Returns selected envelopes and their linked work-item metadata. Read only relevant
plan/request/contract/role/source afterward. show navigates; it does not issue work
or prove Jira data is current.

## Scope audit

```text
python <CONTROL_ROOT>/tools/validate.py audit --control-root <CONTROL_ROOT> --code-root <WORKTREE> --agent <AGENT-ID> --task <TASK-ID> --working-tree
```

Includes changes since base, staged/unstaged changes and untracked nonignored files.
Renames count as deletion plus addition; both paths must be authorized.
Source owners configure legitimate ignored outputs; do not hide changed source.

To inspect a frozen candidate in a readable checkout:

```text
python <CONTROL_ROOT>/tools/validate.py audit --control-root <CONTROL_ROOT> --code-root <CHECKOUT> --agent <SOURCE-AGENT-ID> --task <TASK-ID> --head <CANDIDATE-SHA>
```

agent identifies whose diff is evaluated, not the caller's role. Master can inspect
worker commits without becoming the worker. Integration scope is the named-source
union; their exact commits must appear in candidate history. Workspace and QA
tasks have no source write scope. Candidate QA additionally requires exact assigned
HEAD/base SHA. Review epic environments and workspace output receipts separately.

Exit codes: 0 pass, 1 detected issue, 2 input/inspection failure (re-read records).
The tool does not run registered commands or implement session triggers, timers or Jira writeback.

## Test the guard

```text
python -B -m unittest discover -s <CONTROL_ROOT>/tools -p 'test_*.py' -v
```

Tests use disposable local control/Git fixtures, not the user's repository/Jira.
See ../../VALIDATION.md for current results and limits.

## Review and enforcement limits

Local receipt fields cannot authenticate a real comment, prove complete live Jira
hierarchy, current target status, prose approval scope, immutable history, TDD
chronology, live-session identity or business correctness. Master/integration
must fetch real current sources and review exact evidence. Protect snapshots,
published plans and terminal receipts from silent rewrites.

Prompt boundaries and audits are not filesystem permissions. For stronger
enforcement use OS/tool restrictions and trusted CI with a protected registry
snapshot/guard, then branch protection. Worker-modified guards/self-selected CI
roles are not authorization boundaries. CI and boundary-runner/timer wiring are not installed.
