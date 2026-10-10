# Development policy

Revision: 4
Maintainer: MasterAgent, applying user-authorized policy changes only.

## 1. Authority and ownership

Honor the runtime's higher-priority instructions. Within this project, the user's
explicit direction governs; Master delegates within it, and workers follow issued
assignments. Document conflicting project instructions and resolve them before
dependent edits. Do not interpret a suggested approach as permission to expand scope.

| Resource | Writer | Readers |
| --- | --- | --- |
| `communication/USER.md` | User / UserAssistant | All roles as needed |
| `communication/MASTER.md` | MasterAgent | All roles as needed |
| Policy, index, project map, glossary, registry, task and contract records | MasterAgent | All roles as needed |
| `agents/<id>/AGENT.md`, `agents/<id>/archive/` | That agent | Master and relevant agents |
| `archive/master/` | MasterAgent | All roles as needed |
| Application code, executable tests, migrations, source configuration | Registered path owner under an assigned task | All roles as needed |
| Executable control tooling | Explicitly assigned tooling worker | All roles as needed |
| Jira request text, Archive activation, plan/final decisions | User | Relevant roles |
| Master-owned Jira plan/progress/QA comments and permitted transitions | Master through scoped integration | Relevant roles |
| Intake snapshots and published plans | Master; published revisions immutable | Relevant roles |
| Independent QA record, report and evidence | Assigned QA agent | Master / user / relevant owners |
| Boundary-runner code, local deadline queue and write outbox | Assigned tooling/operator role | Master reads delivered events |

Master may initialize a NEW agent record from the template. Once handed off, only
that agent edits it. To change its charter, Master issues a charter revision in
the registry; the agent updates its own record and acknowledges the revision.
Master never repairs another owner's file, even when its contents are incorrect.

QA is an independent specialization with no source ownership. It inspects and
runs registered safe checks, reports findings in its own files, and never fixes
code, edits tests, impersonates acceptance or sets Jira Done. Master coordinates
quality; the QA agent supplies the report; the user makes the final decision.
Read JIRA_WORKFLOW.md for current plan, QA and acceptance gates.

Master may run inspection, builds, tests, and local disposable application
instances. Use registered verification commands and isolated output directories,
ports, caches, and test data. A test command that updates snapshots, generated
source, production data, or source configuration is a write task for a worker.
Master does not merge, cherry-pick, apply patches, rebase, create code worktrees,
commit source changes, deploy, or fix code. An assigned IntegrationAgent or human
performs source-repository mutations. Production actions need explicit task authority.

## 2. Durable knowledge and context

Keep one canonical `CONTROL_ROOT` outside source worktrees. Do not maintain or
merge competing copies. All chats must be able to read it; grant only the write
access needed for their own records. Keep it versioned or backed up separately.

Executable control tooling changes use an assigned versioned source copy in a
tooling worktree. The operator installs the reviewed version into CONTROL_ROOT
under approved setup authority. Never make CONTROL_ROOT a worker source worktree
or fork canonical coordination records with the tooling source.

Start with INDEX; load your assignment and relevant sources, not every agent's
history. Jira owns product requests, approvals and delivery status; USER owns
standing direction and global decisions. Registry is the authoritative ownership
and internal task-state index, with local Jira observation/decision receipts. Task
Markdown supplies acceptance criteria and rationale; worker records supply
reports. Avoid duplicate editable representations of the same state.

Label facts `confirmed`, `proposed`, `unknown`, or `stale`. Support confirmed
claims with a source path and symbol, user request/decision, or command evidence.
Use code/schema/tests to establish observed behavior; use approved requirements
and contracts to establish required behavior. A mismatch is work to resolve,
not permission to silently redefine either. Verify relevant facts against the
assigned code revision; do not treat an old index as current proof.

Find existing code before adding new code. Search by domain terms and symbols;
follow the path owner and contract links. Verify dependency APIs against the
installed/locked version and primary documentation when needed. Never invent
files, endpoints, capabilities, test results, or unresolved business rules.

## 3. Assignments and concurrent work

Only Master issues or changes task envelopes in REGISTRY.json. Every task has
one assignee, a revision, a Jira request revision and approved plan/digest, a base commit, an explicit
branch/worktree, path scopes, and acceptance criteria in its linked Markdown.
Bind relevant contract revisions; unrelated registry updates do not invalidate a task.
Set `completion_target` to `local` or `promoted` from the requested outcome.
Local completion verifies the deliverable without granting target promotion.

USER requests remain valid for read-only bootstrap/global direction; product
execution requires an approved current Jira plan. Archive permits no execution.
Disabled/unavailable Jira does not prevent authorized documentation/read-only
bootstrap, but cannot authorize implementation. Human/operator bootstrap installs
the source entry point and initial Git commit before task worktree issuance.
Backlog permits inspection, clarification and proposals, not implementation or
Git setup. To Do, In Progress and QA have the gates in JIRA_WORKFLOW.md. A board
move is not approval. Stop/checkpoint affected work when changed intent invalidates
bindings; replan before resuming. Priority-only changes may reorder unchanged work.

QA tasks use kind: qa, completion_target: local, no write_paths or merge_sources,
and an independent QA assignee. Pin the exact candidate/epic subject and safe
verification profiles. Master reserves a unique `qa_report_ref` before issuance;
QA uses that exact report ID/revision. Report production is a milestone, not acceptance.

Worktree preparation can be a `workspace` task for the IntegrationAgent. It uses
an existing operator checkout and names the exact output branches, absolute
worktree paths, and base SHAs. It grants only those Git setup operations, no
source edits, merges, deletion of existing work, or target promotion. Master
verifies the resulting roots, branches, SHAs, and clean status before issuing
feature tasks. Workspace completion is local and needs no application commit.

Every path has one write owner. Domains own their business behavior across
their assigned layers; layer agents own shared technical assets. The two axes
are navigation metadata, not overlapping permission. Use exact files or
directory prefixes ending in `/`; no globs, broad repository grants, or precedence tricks.

Master reserves scopes before setting a task `ready`. Overlapping reservations
are not allowed, even in separate worktrees, except the explicit frozen-source
handoff to an integration task. Shared libraries, schemas, root dependency
files, lockfiles, and generated artifacts also need owners and reservations.

A worker acknowledges the task revision, charter revision, base commit, contracts,
session ID, and roots in its own record before editing. Only one live session
may use that agent ID. Do not take over an apparently idle session based on time
alone. Master records a user-confirmed stop/handoff or explicit session release
before another session resumes it; preserve uncommitted work and checkpoint evidence.

Re-read the relevant task, policy revision, cancellation state, and contracts at
phase boundaries. If your assignment changes, is cancelled, or becomes blocked,
stop dependent writes and checkpoint. A blocked task retains its reservation
until Master explicitly releases, narrows, or cancels it. Do not bypass a dependency.
Its old issued request/policy/charter/contract receipts remain historical while
paused and grant no writes. Revalidate and reissue current bindings, then obtain
acknowledgement before resuming. Independent valid tasks may continue.

Communicate cross-owner requests in your own record with task/contract IDs,
evidence, impact, and the specific answer needed. Master routes them and updates
its records. Do not edit a peer's code or record, or redefine an interface privately.
Manual chats do not notify each other automatically: return the owned report
reference to the sole Master chat for a milestone reconciliation. Without Jira
read access, obtain Master's fresh startup receipt for this launch (UTC, key,
current digest and plan); otherwise pause writes.

## 4. TDD and lean implementation

For changed behavior and bug fixes: write a behavior-focused test; execute it
and capture a meaningful failure; implement the smallest clear solution; run
the test and affected regression checks; refactor while they remain green.
An import, setup, or connectivity failure is not evidence of the expected red.
Keep test names, commands, outcomes, timestamps, and code revisions in the handoff.

Use tests that detect observable mistakes, including applicable boundary and
failure cases. Do not weaken existing tests or change expected behavior merely
to obtain green. Investigate failures against requirements. Prefer real contract
checks over mocks when verifying interaction between subsystems.

Documentation-only, formatting-only, and purely cosmetic changes may use an
appropriate diff, render, or existing validation check rather than artificial
new tests. Record the reason. If legacy code needs characterization before a
safe change, declare the plan. Any exception for a behavior change requires an
explicit Master decision; report the remaining verification gap.

Lean means simple and maintainable, not minimum line count. Reuse suitable
existing code, keep responsibilities clear, avoid speculative abstractions,
unrequested dependencies, unrelated refactors, and elaborate fallback paths.
Use established formatting/lint/type checks; do not impose arbitrary file-size
limits or coverage percentages as substitutes for design and behavior evidence.

## 5. Review, integration, and completion

Workers submit an immutable commit SHA plus evidence and stop modifying that
candidate. `review` means submitted; `verified` means Master checked the local
candidate against its criteria; neither means merged or end-to-end complete.

IntegrationAgent may combine ONLY the exact verified source commits named in
an integration task. Its temporary authority covers their recorded paths for
that merge, not new implementation. Source workers remain paused. Semantic
conflicts and new defects go back to the path owner under a revised/new task.
Rebuild the candidate after a source revision; do not claim an old test run
verified different code. Keep integration candidates separate from feature work.

Master tests the combined candidate, verifies producer and consumer expectations,
and records findings. Master then assigns independent QA on the frozen delivery
subject; QA owns the report. A passing report remains Jira QA until the user
accepts that exact current report, requirement digest, plan and delivery subject.
Fail/skipped mandatory checks cannot satisfy Done. Changed code/report invalidates
old acceptance. Close linked execution assignments before Jira Done.

For an internal task's `completion_target: local`, Master may mark that task done
after its requested technical milestone and relevant checks pass. Record the
exact candidate and completion evidence, release reservations, and retain the
frozen receipt. This does not imply a target changed. An integration task using
a completed candidate must reacquire its historical scopes; current work wins
over an attempt to reuse a released reservation.

For `completion_target: promoted`, IntegrationAgent promotes the exact verified
candidate only after current passing independent QA, final human acceptance,
recorded user-derived promotion authority, and target freshness. If the target
changes or conflicts appear, rebuild and obtain renewed QA/acceptance. Master marks done only
after observing promotion and the required checks. Record the promoted SHA and
authority on the integration task and affected source tasks; the combined SHA
may differ from a source candidate. Deployment is a separate authorized task.

Use bounded states: `draft`, `ready`, `running`, `blocked`, `review`, `verified`,
`integrating`, `done`, `cancelled`. Master writes task state; workers write
observations. Reservations persist for all nonterminal issued states.
Internal `done` means the assigned technical milestone was verified, with a
Master evidence reference; it never silently means deployed or user-accepted.
Workspace tasks use setup receipts; QA tasks use report receipts instead of a
new source candidate. Jira Done separately requires current passing QA, explicit
user acceptance, and any agreed promotion evidence. Epic Done also requires the
complete current child set accepted Done and an accepted QA rollup.
Keep terminal task envelopes and candidate receipts immutable. Follow-up work
gets a new task ID, linked to the original; do not reopen a completed task and
overwrite the source SHA used by earlier integration evidence. Historical scopes
record past authority, not permission under a changed current ownership map.
Historical promotion-authority receipts likewise survive replans; they never
authorize new execution or another promotion.

## 6. Record maintenance and protocol changes

Keep current records brief: active work, open questions, current decisions,
latest evidence, and the next action. Archive completed detail under the writer's
own archive prefix and link it. Preserve request IDs, decision authority, and
verification SHAs. Do not write long speculative reasoning or repeat shared policy.

Use `RQ-0001`, `DEC-0001`, `TASK-0001`, `CON-0001`, `PLAN-0001`, `QA-0001`, Jira keys,
and revision numbers. User/UserAssistant allocates USER request/decision IDs;
Master allocates plan/task/contract IDs and reserves QA report revisions globally.
Agent IDs identify writers; QA report IDs identify reports. Never reuse an ID for
different work or assign the same QA report revision to two tasks.
Master acknowledges request revisions instead
of editing their statuses in USER.md. UserAssistant records answers there;
Master consumes them into its own decision/assignment records. Per-item approvals
and final acceptance are authenticated Jira comments, not invented local decisions.

Policy/ownership-model changes require an explicit user decision. Record the
reason, affected tasks, migration, and new policy revision; do not silently
change the foundation. Project facts, commands, ownership entries, and indexes
must evolve as the repository evolves. Revalidate affected records with changes.

These documents and the supplied validator are coordination and review controls.
They do not provide filesystem permissions, prove TDD chronology, or make CLI
chats communicate automatically. Jira reads occur only at session startup, clear
user milestone/end, or one unanswered-checkpoint timeout (150 minutes default).
No recurring polling/webhook wake-ups. Local assignment checks continue during
work. A running wrapper/timer must deliver one queued timeout to the sole Master;
it cannot infer approval, completion or session release. Follow JIRA_WORKFLOW.md.
Only new real user input can permit rearming after a consumed checkpoint;
automatic summaries or worker reports cannot create another timeout in that silence.
It must not edit Master-owned records itself. Apply actual sandbox/access controls and trusted
CI gates where needed; never claim those are installed by this template.
