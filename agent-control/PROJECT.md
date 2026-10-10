# Verified product and repository map

Writer: MasterAgent. Populate from user direction and observed repository facts.
Do not choose a stack or prescribe a directory restructure from this template.

## Product context

- Intended users and outcome: unknown; see USER.md product brief.
- Current milestone / request: RQ-0001, protocol bootstrap.
- Product requirements source: <actual Jira item/revision, selected snapshot and approved plan>
- Standing direction source: USER.md; keep unknown business facts unknown.
- Jira/boundary-runner state: <confirmed access/mappings/runner evidence, or not installed>
- Independent QA owner: <registered QA ID; no source write ownership>
- Established stack and versions: <verified manifest/lockfile references, or unknown>
- Architecture style / constraints: <confirmed sources, or unknown>
- Deployment status: <observed and sourced, or unknown>

## Code navigation

| Capability / asset | Domain | Layer | Owner ID | Source path and entry symbols | Verification source | Verified at |
| --- | --- | --- | --- | --- | --- | --- |
| <actual capability> | <domain> | <layer> | <registry ID> | <repo-relative path / symbols> | <test path / schema / user requirement> | <code SHA or requirement revision> |

Registry owns permissions. This table routes readers to meaningful entry points
without reproducing the complete file tree. Add a route when it becomes useful;
remove or mark stale routes when their implementation changes.

## Architecture and boundary decisions

| Relationship | Required invariant | Contract / decision | Actual implementation | Verification gap |
| --- | --- | --- | --- | --- |
| <producer → consumer> | <actual approved expectation> | <link / revision> | <source and observed code SHA> | <none or explicit> |

Separate required behavior from observed behavior. Do not describe planned code
as implemented. Shared technical layers should expose defined boundaries rather
than invite every domain agent to modify their internals.

## Verification profiles

Register command profiles in REGISTRY.json after checking real scripts/manifests.

| Profile ID | Purpose | Commands source | Environment / isolation | Verified at |
| --- | --- | --- | --- | --- |
| <actual ID> | <unit / contract / integration / lint / type / UI> | <manifest/script or installed tool/version + command> | <fixtures, isolated ports/output, no production writes> | <SHA + UTC> |

No `npm test`, `pytest`, Maven command, coverage target, or cloud provider is
assumed. Workers propose missing commands; the technical owner implements setup
when needed. Master inspects and registers what actually exists.
An empty repository may start with verified source-preserving Git checks for its
approved scaffold task. Register the actual test harness once its owner supplies
it, before feature behavior work. A whitespace check is not a behavior test.

Independent QA uses confirmed master_safe profiles with disposable outputs and
no source changes. Source/test setup changes belong to an assigned source owner.

## Open knowledge gaps

| Gap | Evidence / why it matters | Responsible role | Affected work | Resolution source |
| --- | --- | --- | --- | --- |
| Product/stack not supplied | Starter template contains no application facts | User / Master discovery | Initial routing and commands | <pending> |
