# Validation contract

| Invariant | Check in synthetic demonstration | Failure response |
|---|---|---|
| Each source ID is unique | Duplicate source ID rejected | Abort plan |
| Each decision refers to a known source | Unknown ID rejected | Abort plan |
| A selected record has not changed source | Expected source compared to inventory | Abort plan |
| Destination exists | Destination checked in folder inventory | Abort plan |
| Unclassified messages remain unchanged | Only explicit plan items are simulated | Preserve source |
| All identities survive a simulated migration | Before/after ID sets compared | Reconciliation error |
| Final location matches decision | Every ID checked against planned destination | Reconciliation error |
| Source data are not mutated | Copy-on-write simulation | Test failure |

## What these checks do not prove

- They do not validate a live Outlook mailbox or the current state of any remote object.
- They do not provide transactionality, rollback, API rate-limit management, or retry guarantees.
- They do not establish that a categorisation rule is semantically correct.
- They do not certify external-system behaviour. The demonstration does not call external APIs.

The purpose is to make data-integrity requirements concrete, inspectable and testable.
