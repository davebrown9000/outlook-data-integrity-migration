# Methodology and system design

## 1. Inventory and analytical assessment

The private implementation recursively enumerated Outlook mail folders and paginated message metadata through Microsoft Graph. It requested the immutable-ID preference and constructed folder and sender-domain summaries to guide restructuring decisions. The inventory supported assessments of archive distribution, unread volume and automation candidates. No live inventories or message-level exports are included here.

## 2. Rule rationalisation and target taxonomy

Existing folder and rule configurations were examined separately from the message inventory. The objective was a maintainable hierarchy and category-oriented automation rather than a collection of overlapping historical rules. The public case study does not disclose the original personal taxonomy or real sender-domain matching logic.

## 3. Preview before mutation

The project used classification/migration previews to make proposed destinations reviewable. A candidate should carry source identity, current source folder, proposed destination, and whether a move is necessary. Ambiguous records remain for review rather than being forced into an arbitrary category.

## 4. Immutable identity and live validation

The private project recorded an operational issue: persisted message identifiers can become stale after mutations. The curated workflow therefore requested Outlook immutable IDs and validated every selected source message and destination folder live before proceeding. Invalid batches were stopped prior to mutation. The public module models these invariants with fictional stable identifiers; it does not make Microsoft Graph calls or promise identical behaviour to the service.

## 5. Execution controls

The private executor's default was dry-run. Write execution required both a command-line execution flag and an independent write-enable setting, after reviewing the intended batch. This protected against accidental mutations but did not make a real batch atomic: remote writes can still fail partway. A robust operational procedure records individual results and reconciles partial successes rather than assuming that preflight prevents all runtime faults.

## 6. Reconciliation and exception review

Identity sets, total counts, per-folder counts and planned destinations provide separate checks. Matching totals are necessary but insufficient: one missing and one duplicated record can cancel out numerically. Stable-ID set equality and destination verification address that weakness. Exceptions should remain reviewable, with reruns based on current state rather than blindly replaying stale plans.

## Public reconstruction boundary

`demo/migration.py` is an independently developed, small offline simulation that illustrates the design decisions. It intentionally omits network access, authentication, retry loops, real classification rules, actual folder names, deployment concerns and mailbox-changing methods. The fictional `stable_id` is not a real Outlook ID or a replacement for documented Microsoft Graph behaviour.
