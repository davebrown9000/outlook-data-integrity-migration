# Outlook Data Integrity & Migration

A synthetic, independently authored case study of **mailbox inventory, deterministic classification, migration safety and post-migration reconciliation**. The engineering emphasis is preserving identity and recoverability while reorganising a large, historically accumulated information store.

## Project context

The underlying private project addressed the audit and restructuring of a substantial Outlook mailbox. The work involved recursive mailbox/folder inventories, rule review, category design, migration previews, controlled execution and validation. The original Microsoft Graph scripts, mailbox identifiers, messages, subjects, folder taxonomy, operational logs and private history are **not published** here.

## Engineering questions

1. How can a large, inconsistently organised mailbox be inventoried without losing provenance?
2. How can message identities remain stable across moves and subsequent validation?
3. How should preview decisions be checked against the live source and destination before changes?
4. How can a migration be checked for completeness, correct destinations and unchanged records?
5. How should ambiguous or unmatched messages be handled without forcing a classification?

## End-to-end architecture

```mermaid
flowchart LR
  A[Read-only mailbox inventory] --> B[Folder and rule analysis]
  B --> C[Category and migration design]
  C --> D[Migration preview]
  D --> E[Identity and destination validation]
  E --> F[Explicitly authorised execution]
  F --> G[Post-execution reconciliation]
  G --> H[Exceptions and review]
```

The diagram describes the **private project's design pattern**. The public executable illustrates the preview and reconciliation stages entirely offline. It never connects to or changes a mailbox.

## Technical decisions demonstrated

- **Stable identity:** model records with stable IDs; the private project specifically requested Outlook immutable IDs to reduce stale-identifier problems when messages moved.
- **Preflight validation:** reject missing sources, stale source folders, duplicate IDs and nonexistent destinations before any move is planned.
- **Dry-run by default:** produce a plan and simulated results without mutating source records or external systems.
- **Conservative classification:** leave records without approved routing decisions untouched.
- **Reconciliation:** compare complete sets of message IDs before and after; check destinations and folder totals.
- **Auditability:** generate a readable move plan and counts that can be independently checked.

## Run the synthetic demonstration

Python 3.11 or later, standard library only:

```bash
python3 -m unittest discover -s tests -v
python3 -m demo.migration --input data/fictional_mailbox.json
```

The sample contains four fictional messages. Two are planned moves, one is already in the correct destination, and one remains unclassified and unchanged. These are **illustrative results, not real mailbox statistics**.

## Further documentation

- [Engineering methodology](docs/methodology.md) — source-of-truth decisions, workflow stages, safeguards and limits.
- [Validation model](docs/validation.md) — invariants and failure modes.
- [NOTICE.md](NOTICE.md) — provenance and rights.

## Scope and rights

No live Microsoft Graph requests, authentication, message mutations, personal information, historical exports or production code are included. The public module models a hypothetical migration, not Microsoft's API response semantics. **Copyright © 2026 David Brown. All rights reserved.** No open-source licence is granted.
