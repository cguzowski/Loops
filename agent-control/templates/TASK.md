# TASK-<ID> — <observable outcome>

Task ID: TASK-<ID>
Revision: <n>
Writer: MasterAgent only.

## Assignment envelope

Read this task's entry in REGISTRY.json for assignee, state, path reservations,
base commit, branch/worktree, dependencies, contract revisions, and verification
profiles, kind, completion target, request_ref, plan_ref and requirements_digest.
QA tasks also bind qa_subject, qa_subject_digest and Master's reserved qa_report_ref.
Those fields have one live source. This document's revision must match
the envelope. Worker observations belong in the worker's own record.

## Intent and authority

- Jira request / revision: <KEY@revision and immutable requirement snapshot>
- Approved plan / approval source: <PLAN-ID@revision; actual human Jira comment>
- Requirement digest: <canonical snapshot hash>
- Why this change is needed: <specific problem>
- Expected observable result: <behavior / actual deliverable>
- Requested milestone: <local candidate / promoted source target / workspace outputs>
- Exclusions / constraints: <what is outside this assignment>
- Relevant decision sources: <DEC IDs, or none>

## Context packet — load only these relevant sources

| Source | Why it matters | Revision / verification |
| --- | --- | --- |
| <source path + symbol> | <existing implementation / invariant> | <code SHA> |
| <contract reference> | <producer or consumer expectation> | <pinned revision> |
| <test / requirement source> | <behavior to preserve> | <SHA / user revision> |

List confirmed facts, proposals, and unresolved facts separately. Missing source
is not evidence that a new component is necessary.

## Acceptance criteria

| ID | Required outcome / example | Expected verification | Responsible reviewer |
| --- | --- | --- | --- |
| AC-1 | <concrete normal behavior> | <behavior test / command profile> | <Master review; independent QA> |
| AC-2 | <relevant error, access, isolation, or boundary case> | <actual appropriate check> | <Master review; independent QA> |
| AC-3 | <existing behavior preserved> | <affected regression checks> | <Master review; independent QA> |

Use only relevant criteria. Do not invent SaaS features, tenant semantics,
latency requirements, or regulatory obligations from the template.

## Implementation guidance

- Existing pattern to reuse: <path and symbol, or needs discovery>
- TDD plan: <smallest meaningful red → green → refactor sequence>
- QA task: <pinned delivery subject; safe checks; report only, no implementation>
- QA report identity, when assigned: <Master-reserved QA-ID@revision; owned archive path>
- Nonbehavioral verification exception, if applicable: <reason and check>
- Boundary coordination: <owner questions/acknowledgements that must be resolved>
- Documentation/navigation update expected: <owner proposes; Master applies>

Prefer outcomes and constraints over prescribing every implementation step.
For substantial work, add a short sequence with independently verifiable steps;
for a small task, this record is sufficient without a second planning document.

## Review and handoff

- Worker report: <agents/ID/AGENT.md section>
- Required submission: immutable candidate SHA, acceptance evidence, scope audit,
  relevant regression results, boundary changes, unresolved gaps, next action.
  For workspace tasks, submit observed declared output roots/branches/base SHAs
  and clean status instead of an application candidate.
  For QA tasks, submit an owned QA_REPORT with the exact subject digest and
  executed evidence instead of a new code commit. A failed QA report can be a
  completed report task; it does not satisfy delivery acceptance.
- Master findings: <specific criterion/evidence, or pending>
- Correction/reissue history: <revision and rationale>
- Integration task / final verdict: <references; never equate submitted with done>
- Completion evidence: <Master verdict for the envelope's local/promoted target>

Internal task completion does not move Jira Done. The delivery requires current
passing independent QA and explicit user acceptance, plus any authorized promotion.
