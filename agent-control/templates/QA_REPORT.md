# QA-<ID> — <Jira key and reviewed outcome>

Report ID: QA-<ID>
Revision: <n>
Writer: <QA-AGENT-ID> only. Freeze submitted report revisions.
Use the exact Master-reserved qa_report_ref from the task. The agent ID names
the writer; Report ID names this report. Never overwrite a submitted revision.

## Subject and environment

- Jira item / QA task / approved plan: <exact references>
- Requirements revision/digest: <current binding>
- Review subject/digest: <registry qa_subject / qa_subject_digest>
- Candidate SHA / target base: <exact code revisions or epic child receipts>
- Environment, fixtures, versions, UTC: <actual setup; source preserved>
- Examined scope / material exclusions: <actual coverage>

## Acceptance and regression evidence

| Criterion / check | Command or manual steps | Expected | Actual observed result | Evidence / revision |
| --- | --- | --- | --- | --- |
| <AC-ID> | <executed check> | <required behavior> | <pass/fail/blocked and observation> | <log/artifact/SHA/UTC> |

Distinguish reviewed worker evidence from checks you independently executed.
Name skipped checks and causes. Zero discovered tests or setup/import failures
are not evidence that intended behavior passed.

## Findings

| Finding ID | Reproduction / expected vs actual | Impact / criterion | Source owner | Evidence / disposition |
| --- | --- | --- | --- | --- |
| <F-ID> | <minimal reproducible case> | <specific> | <registered owner or needs routing> | <open / fixed in new subject / verified> |

## Verdict and user review

- Verdict: <pass / fail / blocked>
- Reason: <supported criteria; mandatory gaps prevent pass>
- Remaining gaps / limitations: <specific or none>
- User QA preview/demo/steps: <actual accessible result>
- Recommendation: <ready for acceptance / owner correction / missing prerequisite>
- Supersedes: <prior report revision and subject or none>

User accepts in Jira with `ACCEPT QA-<ID>@<revision>` or requests changes. QA
never fills a user approval or sets Jira Done. Master records genuine decisions
and observed delivery separately.
