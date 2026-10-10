# Foundation validation

Checked 2026-10-10. Version 1.2.1 uses disposable local fixtures; no user
application repository or Jira account was connected or changed.

## Automated checks

All 57 tests pass:

```text
python -B -m unittest discover -s agent-control/tools -p 'test_*.py' -v
```

Coverage includes ownership/reservation conflicts, concurrent record/worktree
collisions, stale revisions, contracts, dependency cycles, untracked/renamed
foreign paths, governance authority, immutable historical scopes, bounded
workspace setup and local/promoted technical completion. A real local Git
integration fixture preserves two exact independently committed source histories.

Jira/QA and synchronization checks cover:

- Session-boundary mode; periodic polling and Jira-change triggers rejected.
- Inactivity timeout restricted to the requested two-to-three-hour range.
- Exact requested seven-column order.
- No Archive execution; no To Do execution without current human plan approval.
- Bot approval/final-acceptance receipts rejected.
- Material requirement changes invalidate old plans.
- USER-file requests cannot bypass Jira execution gates.
- Independent QA, empty source write authority and exact request/candidate/base.
- Passing QA remains pending human acceptance.
- Failed QA cannot satisfy Done.
- Changed candidate/report invalidates earlier evidence/acceptance.
- Promoted Done requires exact observed-promotion fields.
- Epic rollups bind accepted child receipts; reopened children invalidate Done.
- Real Git QA checkout accepted unchanged; source edits rejected.
- Readiness requires a registered independent QA specialist.
- Windows worktree case/slash aliases cannot acquire separate reservations.
- Safely paused stale work preserves its reservations while independent work proceeds.
- A historical promotion receipt survives a later replan without granting new authority.
- Unresolved Backlog completion targets may remain unknown rather than guessed.
- Current delivery completion cannot borrow terminal tasks from another request.
- QA reports match uniquely reserved IDs/revisions, including across concurrent QA tasks.
- Final QA acceptance alone cannot authorize source promotion; explicit promotion does.

Behavior guards were developed with failing regression checks before fixes.
The initial workflow implementation had eleven expected failing gate tests; the
later review added three failing bypass/base-binding regressions before correction.
Three synchronization-configuration regressions were also added failing before
replacing the polling guard. The final suite is green.
This review added ten checks: nine reproduced guard failures before corrections,
and one confirmed explicitly approved exact-candidate promotion remains valid.

## Procedure review

Reviewed the full pack for role ownership, narrow context routing, TDD evidence,
concurrent session/worktree reservations, request/plan/report identity, pause/resume,
local versus promoted completion, and timer consumption. Clarified the empty-repo
bootstrap and manual worker → Master → QA → human-decision sequence. Documentation
and read-only discovery may begin before Jira is available; implementation may not.
Automatic summaries cannot rearm a consumed timeout during the same silence.

## Artifact checks

The final pack checks local Markdown file links, JSON/Python syntax, the exact
two communication Markdown files, structural validation and ZIP integrity.
The empty starter is structurally valid and intentionally fails readiness.

Templates remain unfilled where product paths, owners, commands, account mappings
or real user decisions must be discovered. Examples are not actual approvals.

## Runtime limits

This update was not tested against a live Jira board, credentials, boundary
runner, actual user-idle timer, Codex CLI binary or running QA-agent session.
JIRA_SETUP.md lists the required disposable live integration checks.
The pack specifies that service; it does not install it.

Version 1.0 had fresh isolated Master/implementation-worker protocol trials.
Those trials predate this Jira/independent-QA update and do not validate the new
approval/QA workflow end to end. No new runtime claim is inferred from them.
The procedural review is a consistency review, not a live multi-chat trial.

Passing local tests establishes guard behavior on fixtures. It does not enforce
filesystem permissions, authenticate real approvals, prove TDD chronology,
complete Jira pagination or establish correctness of an unconfigured SaaS.
