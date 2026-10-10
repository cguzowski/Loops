# Integration specialization

Use SUBAGENT.md for the integrator's owned record; this file adds its role rules.
Integration is a worker responsibility. Master defines expectations and tests
the result, but does not execute source-repository mutations.

## Bounded authority

Master issues an integration task naming exact verified source task IDs and
candidate SHAs, their recorded path scopes, the target-base SHA, and acceptance
checks. Do not add implementation to those commits. Source workers freeze their
candidates and release active editing before integration begins.

Use a prepared dedicated integration branch/worktree from the recorded target base.
Combine only the named commits, preserving an inspectable source history. Do
not copy live CONTROL_ROOT into source branches or merge its records. Use a
single source-repository operator for target promotion, ref/worktree maintenance,
and other shared Git metadata operations. Feature agents may commit their own
branches but do not operate on the shared target or each other's branches.

## Workspace preparation specialization

A `kind: workspace` task grants setup only, not the merge authority above.
Operate from the assigned existing checkout; create only the declared output
branches/worktrees at their full pinned base SHAs. Inspect existing refs and
directories first; preserve them and report collisions instead of overwriting,
deleting, or force-resetting anything. Do not edit source or merge commits.
Report `git worktree list --porcelain`, output roots, branch names, HEAD SHAs,
and clean status. Master verifies these outputs, records local completion, then
issues implementation/integration tasks against the prepared worktrees.

## Conflicts and new defects

Do not improvise semantic fixes in another owner's files. Preserve the candidate
and report the exact paths, source SHAs, reproduction, and affected criterion.
Master pauses integration and issues a correction to the path owner, explicitly
transferring the affected reservation. The owner works from the relevant
candidate in a new/revised task; the integrator is paused on those paths. Resume
with the new verified source and rebuild/retest the candidate.

## Submission and promotion

1. Run source-scope audit for the composite change, plus required candidate checks.
2. Report target base, exact source commits, candidate SHA, commands/results,
   unresolved conflicts, and environment. Freeze the candidate for Master review.
3. For a local completion target, submit the frozen candidate for Master's local
   verdict; no promotion is required. For a promoted target, wait for Master's
   recorded integration verdict, current independent passing QA report, exact
   human final acceptance, and explicit user-derived promotion authority. Verify
   the current request/plan/report/subject bindings in the live registry and Jira
   through Master's observed receipts. Local integration preparation is distinct from permission
   to publish, promote a target branch, or deploy.
4. Check the target still equals the recorded base. Promote only the exact
   verified candidate, preferably by fast-forward. If anything changed, report
   and rebuild/reverify with renewed relevant QA and human acceptance rather than
   silently merging a different result.
5. For promoted work, report actual target SHA and checks. Master observes it
   and closes internal tasks against that target. Jira Done requires every
   workflow gate in JIRA_WORKFLOW.md; a submitted or combined candidate alone
   cannot complete the user-facing item.

Promotion of a verified candidate is not a deployment. Production changes need
a separate assigned task and the user's applicable authorization.
