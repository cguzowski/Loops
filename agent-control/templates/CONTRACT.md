# CON-<ID> — <producer / consumer boundary>

Contract ID: CON-<ID>
Revision: <n>
Writer: MasterAgent only. Freeze this file once agreed and issued; create a new
revision file for changed expectations. Lifecycle state lives in REGISTRY.json.

## Ownership and authority

- Required outcome / Jira request: <KEY@revision and approved PLAN-ID@revision>
- Producer owner and source entry point: <agent ID; actual path/symbol or planned>
- Consumer owner and source entry point: <agent ID; actual path/symbol or planned>
- Public interface / schema source: <actual source when it exists>
- Prior revision / compatibility decision: <reference or first version>

## Required inputs

| Field / signal | Type / format | Required? | Constraints / meaning | Example |
| --- | --- | --- | --- | --- |
| <name> | <precise representation> | <yes/no> | <business semantics> | <valid value> |

Define identifiers, units, time representation, optional/null distinctions,
ordering, and validation where relevant. Mark unresolved choices explicitly.

## Required outputs and errors

| Outcome | Output / error representation | Consumer obligation | Example |
| --- | --- | --- | --- |
| <normal> | <exact shape and meaning> | <expected handling> | <example> |
| <failure> | <error/retry behavior> | <handling> | <example> |

Include relevant authorization/isolation boundaries, side effects, idempotency,
consistency, retry/timeout semantics, or pagination when the actual interface
needs them. Omit inapplicable sections rather than inventing requirements.

## Interaction examples and invariants

- Given <input/state>, producer returns/emits <result>; consumer produces <observable outcome>.
- Given <relevant error>, the expected result is <handling and preserved invariant>.
- Compatibility: <existing behavior preserved / explicit migration>.

## Verification agreement

| Check | Source owner | Executable source / profile | Evidence needed |
| --- | --- | --- | --- |
| Producer behavior | <owner> | <test path/profile, or implementation task> | <actual shape and semantics> |
| Consumer behavior | <owner> | <test path/profile, or implementation task> | <handling> |
| Combined interaction | <owner prepares; Master reviews; independent QA verifies> | <actual integration check> | <real producer/consumer result> |

Owner acknowledgement references live in their agent records; their messages
are not permission to change this specification privately. Master records their
acknowledgements in the registry. Acknowledging the SPECIFICATION does not mean
the IMPLEMENTATION already exists or has passed verification.

## Known unknowns / migration

- Unresolved choices: <none before agreement, or specific questions>
- Affected existing consumers: <verified list or explicit gap>
- Migration/deprecation plan: <if applicable>
- Observed implementation gap: <actual source and code SHA; do not rewrite desired behavior to match a bug>
