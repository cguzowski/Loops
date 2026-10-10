# Glossary and search aliases

Writer: MasterAgent. Add product vocabulary only from actual requirements/source.

| Term | Meaning | Search aliases | Owner / authority |
| --- | --- | --- | --- |
| MasterAgent | Technical PM/coordinator; plans, delegates, reviews and safely tests without source edits | master, coordinator | USER direction; POLICY revision 4 |
| UserAssistant | Personal Codex session that edits only USER.md | user-side Codex | User |
| Domain owner | Registered business capability owner across assigned layers | capability owner | Registry and verified source map |
| Layer owner | Registered shared technical asset owner | platform owner | Registry and source map |
| Path owner | One agent permitted to change exact file/prefix | write owner | Registry scopes |
| QAAgent | Independent verifier/report owner with no source write ownership | QA, tester | QA specialization and issued task |
| Archive | Ordinary visible status for user-parked work; no execution | parked idea | User activation |
| Approved plan | Exact current plan bound to requirement digest and genuine human Jira approval | PLAN-ID@revision | Actual human comment |
| Requirement digest | Canonical JSON hash of selected material user intent | requirements_digest | Immutable snapshot; live Jira reconciled |
| Contract | Pinned required producer/consumer boundary with both owners' acknowledgements | interface specification | Master record, owner receipts |
| Task envelope | Internal scope/state/revisions/worktree/base and approved bindings | assignment | Registry, Master writer |
| Candidate | Frozen immutable source commit submitted for review/QA | submitted SHA | Actual Git object and owner evidence |
| Verified | Master checked the technical milestone; user acceptance is separate | local verification | Exact evidence receipt |
| QA subject | Exact candidate/base or accepted epic child receipts being evaluated | qa_subject | Canonical digest and QA task |
| QA report reference | Globally reserved report ID/revision, distinct from the QA agent ID | qa_report_ref, QA-ID@revision | Master reserves; QA writes |
| QA pass | Executed mandatory checks support the exact subject; stays QA pending user | passing report | QA-owned report |
| Final acceptance | Human decision accepting exact current report and subject | ACCEPT QA-ID@revision | Authenticated user comment |
| Internal done | Assigned technical milestone completed; a failed report may still be delivered | task completion | Master evidence; not Jira acceptance |
| Jira Done | Current passing QA, human acceptance and agreed delivery verified | accepted delivery | JIRA_WORKFLOW gates |
| Promoted | Exact tested candidate observed on authorized source target | integration receipt | Integrator action, Master observation |

## Product vocabulary — populate on demand

| Term | Exact business meaning | Aliases/symbols | Domain/layer/owner | Source and revision | Status |
| --- | --- | --- | --- | --- | --- |
| <term> | <specific meaning> | <actual search terms> | <routing> | <requirement or path at SHA> | <confirmed/proposed/unknown/stale> |

Index useful business concepts and ambiguous boundary names, not every class.
Owners submit changed meanings; Master checks approved requirements/contracts.
