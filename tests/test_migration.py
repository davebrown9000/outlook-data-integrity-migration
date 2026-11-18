import json
import unittest
from copy import deepcopy
from pathlib import Path
from demo.migration import MigrationError, plan_migration, reconcile, simulate_plan


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("data/fictional_mailbox.json").read_text())

    def plan(self, data=None):
        d = data or self.data
        return plan_migration(d["messages"], d["folders"], d["decisions"])

    def test_valid_plan_and_unchanged_item(self):
        p = self.plan()
        self.assertEqual([x["action"] for x in p], ["move", "move", "unchanged"])

    def test_unclassified_message_not_moved(self):
        after = simulate_plan(self.data["messages"], self.plan())
        self.assertEqual(next(x for x in after if x["stable_id"] == "fiction-004")["folder"], "Inbox")

    def test_stale_source_prevents_plan(self):
        d = deepcopy(self.data)
        d["messages"][0]["folder"] = "Archive/Reference"
        with self.assertRaisesRegex(MigrationError, "source changed"):
            self.plan(d)

    def test_missing_destination_prevents_plan(self):
        d = deepcopy(self.data)
        d["decisions"][0]["destination"] = "Archive/Missing"
        with self.assertRaisesRegex(MigrationError, "destination folder missing"):
            self.plan(d)

    def test_duplicate_identity_rejected(self):
        d = deepcopy(self.data)
        d["messages"].append(d["messages"][0])
        with self.assertRaisesRegex(MigrationError, "duplicate"):
            self.plan(d)

    def test_missing_source_rejected(self):
        d = deepcopy(self.data)
        d["decisions"][0]["stable_id"] = "absent"
        with self.assertRaisesRegex(MigrationError, "source message missing"):
            self.plan(d)

    def test_identity_and_count_reconciliation(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)
        report = reconcile(self.data["messages"], after, p)
        self.assertEqual(report["before_count"], report["after_count"])
        self.assertEqual(report["planned_moves"], 2)
        self.assertEqual(report["folder_counts_after"]["Inbox"], 1)

    def test_reconciliation_detects_missing_message(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)[:-1]
        with self.assertRaisesRegex(MigrationError, "identity reconciliation"):
            reconcile(self.data["messages"], after, p)

    def test_reconciliation_detects_wrong_folder(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)
        after[0]["folder"] = "Inbox"
        with self.assertRaisesRegex(MigrationError, "destination reconciliation"):
            reconcile(self.data["messages"], after, p)

    def test_reconciliation_rejects_modified_existing_attribute(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)
        after[0]["subject"] = "Unexpected replacement"
        with self.assertRaisesRegex(MigrationError, "record attributes changed"):
            reconcile(self.data["messages"], after, p)

    def test_reconciliation_rejects_added_attribute(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)
        after[0]["unplanned_metadata"] = "introduced"
        with self.assertRaisesRegex(MigrationError, "record attributes changed"):
            reconcile(self.data["messages"], after, p)

    def test_reconciliation_preserves_all_other_fields(self):
        p = self.plan()
        after = simulate_plan(self.data["messages"], p)
        report = reconcile(self.data["messages"], after, p)
        self.assertTrue(report["identities_preserved"])
        before_by_id = {r["stable_id"]: r for r in self.data["messages"]}
        for row in after:
            original = before_by_id[row["stable_id"]]
            self.assertEqual({k: v for k, v in original.items() if k != "folder"},
                             {k: v for k, v in row.items() if k != "folder"})

    def test_input_not_mutated(self):
        before = deepcopy(self.data["messages"])
        simulate_plan(self.data["messages"], self.plan())
        self.assertEqual(self.data["messages"], before)


if __name__ == "__main__":
    unittest.main()
