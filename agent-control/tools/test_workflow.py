"""Jira approval, independent QA, and final user acceptance regressions."""
import json
import unittest
from pathlib import Path
import tempfile

import workflow


class JiraGates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ("work-items", "plans", "agents/qa-agent/archive"):
            (self.root / directory).mkdir(parents=True)
        request = {"summary": "Normalize labels", "acceptance": ["Trim and lowercase", "Reject blank"]}
        (self.root / "work-items/DEMO-1-r1.json").write_text(json.dumps(request))
        (self.root / "work-items/DEMO-1.md").write_text("# Demo intake\n")
        (self.root / "plans/PLAN-0001-v1.md").write_text("Plan ID: PLAN-0001\nRevision: 1\n")
        self.request_digest = workflow.digest(request)
        self.plan_ref = "PLAN-0001@1"
        self.candidate = "a" * 40
        self.registry = {
            "jira": {"enabled": True, "site_url": "https://fixture.atlassian.net", "project_keys": ["DEMO"],
                     "board_columns": workflow.BOARD_COLUMNS, "status_ids": {name: str(i+1) for i, name in enumerate(workflow.BOARD_COLUMNS)},
                     "user_account_ids": ["human-owner"], "master_account_id": "master-bot",
                     "sync_mode": "session_boundaries", "sync_triggers": ["session_start", "milestone", "inactivity"],
                     "inactivity_timeout_seconds": 9000},
            "agents": {"developer": {"specialization": "implementation"}, "qa-agent": {"specialization": "qa", "owns": []}},
            "verification_profiles": {"unit": {"master_safe": True}},
            "tasks": {"TASK-0001": {"assignee": "developer", "kind": "implementation", "state": "ready", "request_ref": "DEMO-1@1",
                                      "plan_ref": self.plan_ref, "requirements_digest": self.request_digest}},
            "work_items": {"DEMO-1": {
                "file": "work-items/DEMO-1.md", "item_type": "delivery", "parent_key": None, "board_status": "To Do",
                "requirements_revision": 1, "requirements_file": "work-items/DEMO-1-r1.json", "requirements_digest": self.request_digest,
                "plan": {"id": "PLAN-0001", "revision": 1, "file": "plans/PLAN-0001-v1.md",
                         "requirements_revision": 1, "requirements_digest": self.request_digest,
                         "approval": {"decision": "approved", "author_account_id": "human-owner", "source_ref": "jira-comment:100",
                                      "plan_ref": self.plan_ref, "requirements_digest": self.request_digest}},
                "execution_tasks": ["TASK-0001"], "completion_target": "local", "candidate_commit": None,
                "qa_task_id": None, "final_acceptance": None}}}
        self.item = self.registry["work_items"]["DEMO-1"]

    def tearDown(self):
        self.temp.cleanup()

    def errors(self):
        return workflow.checks(self.root, self.registry)

    def attach_qa(self, verdict="pass"):
        self.item.update(board_status="QA", candidate_commit=self.candidate, qa_task_id="TASK-0002")
        self.registry["tasks"]["TASK-0001"].update(state="verified", candidate_commit=self.candidate)
        subject = {"kind": "candidate", "issue_key": "DEMO-1", "requirements_digest": self.request_digest,
                   "plan_ref": self.plan_ref, "completion_target": "local", "candidate_commit": self.candidate}
        report_file = "agents/qa-agent/archive/QA-0001-v1.md"
        (self.root / report_file).write_text("Report ID: QA-0001\nRevision: 1\n")
        self.registry["tasks"]["TASK-0002"] = {
            "assignee": "qa-agent", "kind": "qa", "state": "done", "request_ref": "DEMO-1@1", "completion_target": "local",
            "plan_ref": self.plan_ref, "requirements_digest": self.request_digest, "write_paths": [], "merge_sources": [],
            "qa_report_ref": "QA-0001@1",
            "verification_profiles": ["unit"], "qa_subject": subject, "qa_subject_digest": workflow.digest(subject),
            "qa_report": {"id": "QA-0001", "revision": 1, "file": report_file, "verdict": verdict, "subject_digest": workflow.digest(subject)}}
        return self.registry["tasks"]["TASK-0002"]

    def accept(self):
        qa = self.registry["tasks"][self.item["qa_task_id"]]
        self.item["final_acceptance"] = {
            "decision": "accepted", "author_account_id": "human-owner", "source_ref": "jira-comment:101",
            "plan_ref": self.plan_ref, "requirements_digest": self.request_digest,
            "qa_report_ref": "QA-0001@1", "subject_digest": qa["qa_subject_digest"]}
        self.item["board_status"] = "Done"
        for task_id in self.item["execution_tasks"]:
            self.registry["tasks"][task_id]["state"] = "done"

    def test_approved_queue_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_periodic_jira_polling_configuration_is_rejected(self):
        self.registry["jira"].update(sync_mode="polling", poll_interval_seconds=180)
        self.assertTrue(any("session-boundary" in error for error in self.errors()))

    def test_inactivity_timeout_must_be_within_two_to_three_hours(self):
        self.registry["jira"]["inactivity_timeout_seconds"] = 180
        self.assertTrue(any("inactivity" in error for error in self.errors()))

    def test_jira_change_events_cannot_add_a_background_sync_trigger(self):
        self.registry["jira"]["sync_triggers"].append("jira_change")
        self.assertTrue(any("sync triggers" in error for error in self.errors()))

    def test_archive_cannot_issue_execution(self):
        self.item["board_status"] = "Archive"
        self.assertTrue(any("Archive" in error for error in self.errors()))

    def test_to_do_requires_explicit_current_plan_approval(self):
        self.item["plan"]["approval"] = None
        self.assertTrue(any("approval" in error for error in self.errors()))

    def test_bot_cannot_approve_its_own_plan(self):
        self.item["plan"]["approval"]["author_account_id"] = "master-bot"
        self.assertTrue(any("human" in error for error in self.errors()))

    def test_changed_requirements_invalidate_old_plan(self):
        updated = {"summary": "Preserve case", "acceptance": ["Trim only"]}
        path = "work-items/DEMO-1-r2.json"
        (self.root / path).write_text(json.dumps(updated))
        self.item["requirements_file"] = path
        self.item["requirements_digest"] = workflow.digest(updated)
        self.item["requirements_revision"] = 2
        self.assertTrue(any("plan approval needs current requirements" in error for error in self.errors()))

    def test_user_markdown_request_cannot_bypass_jira_execution_approval(self):
        self.registry["tasks"]["TASK-0001"]["request_ref"] = "RQ-0001@2"
        self.assertTrue(any("approved Jira" in error for error in self.errors()))

    def test_closed_qa_task_must_match_its_issue_and_approved_request(self):
        qa = self.attach_qa()
        self.accept()
        qa["request_ref"] = "DEMO-99@1"
        self.assertTrue(any("QA task request" in error for error in self.errors()))

    def test_promoted_qa_needs_exact_target_base(self):
        qa = self.attach_qa()
        self.item["completion_target"] = "promoted"
        qa["qa_subject"] = workflow.subject_for("DEMO-1", self.item, self.registry)
        qa["qa_subject_digest"] = workflow.digest(qa["qa_subject"])
        qa["qa_report"]["subject_digest"] = qa["qa_subject_digest"]
        self.assertTrue(any("target_base_commit" in error for error in self.errors()))

    def test_bot_cannot_accept_qa_for_the_user(self):
        self.attach_qa()
        self.accept()
        self.item["final_acceptance"]["author_account_id"] = "master-bot"
        self.assertTrue(any("final user acceptance" in error and "human" in error for error in self.errors()))

    def test_new_qa_report_needs_renewed_user_acceptance(self):
        qa = self.attach_qa()
        self.accept()
        report_file = "agents/qa-agent/archive/QA-0001-v2.md"
        (self.root / report_file).write_text("Report ID: QA-0001\nRevision: 2\n")
        qa["qa_report"].update(revision=2, file=report_file)
        qa["qa_report_ref"] = "QA-0001@2"
        self.assertTrue(any("final user acceptance" in error and "stale" in error for error in self.errors()))

    def attach_epic(self):
        self.attach_qa()
        self.accept()
        self.item["parent_key"] = "DEMO-2"
        requirement = {"summary": "Catalog milestone", "children": ["DEMO-1"]}
        requirement_digest = workflow.digest(requirement)
        (self.root / "work-items/DEMO-2-r1.json").write_text(json.dumps(requirement))
        (self.root / "work-items/DEMO-2.md").write_text("# Epic intake\n")
        (self.root / "plans/PLAN-0002-v1.md").write_text("Plan ID: PLAN-0002\nRevision: 1\n")
        epic = {"file": "work-items/DEMO-2.md", "item_type": "epic", "board_status": "Done",
                "child_keys": ["DEMO-1"], "requirements_revision": 1,
                "requirements_file": "work-items/DEMO-2-r1.json", "requirements_digest": requirement_digest,
                "completion_target": "local", "execution_tasks": [], "qa_task_id": "TASK-0003",
                "plan": {"id": "PLAN-0002", "revision": 1, "file": "plans/PLAN-0002-v1.md",
                         "requirements_revision": 1, "requirements_digest": requirement_digest,
                         "approval": {"decision": "approved", "author_account_id": "human-owner", "source_ref": "jira-comment:200",
                                      "plan_ref": "PLAN-0002@1", "requirements_digest": requirement_digest}}}
        self.registry["work_items"]["DEMO-2"] = epic
        subject = workflow.subject_for("DEMO-2", epic, self.registry)
        report_file = "agents/qa-agent/archive/QA-0002-v1.md"
        (self.root / report_file).write_text("Report ID: QA-0002\nRevision: 1\n")
        self.registry["tasks"]["TASK-0003"] = {
            "assignee": "qa-agent", "kind": "qa", "state": "done", "request_ref": "DEMO-2@1", "completion_target": "local",
            "plan_ref": "PLAN-0002@1", "requirements_digest": requirement_digest, "write_paths": [], "merge_sources": [],
            "qa_report_ref": "QA-0002@1",
            "verification_profiles": ["unit"], "qa_subject": subject, "qa_subject_digest": workflow.digest(subject),
            "qa_report": {"id": "QA-0002", "revision": 1, "file": report_file, "verdict": "pass", "subject_digest": workflow.digest(subject)}}
        epic["final_acceptance"] = {
            "decision": "accepted", "author_account_id": "human-owner", "source_ref": "jira-comment:201",
            "plan_ref": "PLAN-0002@1", "requirements_digest": requirement_digest,
            "qa_report_ref": "QA-0002@1", "subject_digest": workflow.digest(subject)}
        return epic

    def test_epic_rollup_accepts_exact_completed_child_receipts(self):
        self.attach_epic()
        self.assertEqual(self.errors(), [])

    def test_reopened_child_invalidates_epic_done(self):
        self.attach_epic()
        self.item["board_status"] = "QA"
        self.assertTrue(any("epic QA/Done" in error for error in self.errors()))

    def test_board_order_is_exact(self):
        self.registry["jira"]["board_columns"] = list(reversed(workflow.BOARD_COLUMNS))
        self.assertTrue(any("column order" in error for error in self.errors()))

    def test_qa_pass_stays_pending_without_final_user_acceptance(self):
        self.attach_qa()
        self.assertEqual(self.errors(), [])
        self.item["board_status"] = "Done"
        self.assertTrue(any("final user acceptance" in error for error in self.errors()))

    def test_final_acceptance_of_exact_qa_report_allows_done(self):
        self.attach_qa()
        self.accept()
        self.assertEqual(self.errors(), [])

    def test_qa_failure_prevents_done(self):
        self.attach_qa(verdict="fail")
        self.accept()
        self.assertTrue(any("passing QA" in error for error in self.errors()))

    def test_changed_candidate_invalidates_qa_and_final_acceptance(self):
        self.attach_qa()
        self.accept()
        self.item["candidate_commit"] = "b" * 40
        self.assertTrue(any("QA subject" in error for error in self.errors()))

    def test_qa_agent_cannot_review_its_own_implementation(self):
        self.attach_qa()
        self.registry["tasks"]["TASK-0001"]["assignee"] = "qa-agent"
        self.assertTrue(any("independent" in error for error in self.errors()))

    def test_qa_cannot_have_source_write_authority(self):
        qa = self.attach_qa()
        qa["write_paths"] = ["src/"]
        self.assertTrue(any("QA source" in error for error in self.errors()))

    def test_promoted_done_requires_observed_exact_promotion(self):
        qa = self.attach_qa()
        self.item["completion_target"] = "promoted"
        qa["qa_subject"].update(completion_target="promoted", target_base_commit="c" * 40)
        self.item["target_base_commit"] = "c" * 40
        qa["qa_subject_digest"] = workflow.digest(qa["qa_subject"])
        qa["qa_report"]["subject_digest"] = qa["qa_subject_digest"]
        self.accept()
        self.assertTrue(any("promotion" in error for error in self.errors()))

    def test_backlog_can_retain_an_unknown_delivery_milestone(self):
        self.item.update(board_status="Backlog", plan=None, completion_target=None)
        self.registry["tasks"]["TASK-0001"]["state"] = "draft"
        self.assertEqual(self.errors(), [])

    def test_done_cannot_use_an_execution_task_from_another_request(self):
        self.attach_qa()
        self.accept()
        self.registry["tasks"]["TASK-0001"]["request_ref"] = "DEMO-99@1"
        self.assertTrue(any("execution task binding" in error for error in self.errors()))

    def test_qa_report_must_use_the_master_allocated_identity(self):
        qa = self.attach_qa()
        qa["qa_report_ref"] = "QA-0099@1"
        self.assertTrue(any("allocated report" in error for error in self.errors()))

    def test_separate_qa_tasks_cannot_claim_the_same_report_revision(self):
        import copy
        qa = self.attach_qa()
        self.registry["tasks"]["TASK-0003"] = copy.deepcopy(qa)
        self.assertTrue(any("report revision already allocated" in error for error in self.errors()))

    def prepare_promoted_acceptance(self):
        qa = self.attach_qa()
        self.item.update(completion_target="promoted", target_base_commit="c" * 40,
                         promoted_commit=self.candidate, promotion_authority="jira-comment:100")
        qa["qa_subject"] = workflow.subject_for("DEMO-1", self.item, self.registry)
        qa["qa_subject_digest"] = workflow.digest(qa["qa_subject"])
        qa["qa_report"]["subject_digest"] = qa["qa_subject_digest"]
        self.accept()

    def test_final_acceptance_does_not_implicitly_grant_promotion(self):
        self.prepare_promoted_acceptance()
        self.item["plan"]["promotion_authorized"] = False
        self.assertTrue(any("promotion authority" in error for error in self.errors()))

    def test_current_explicit_plan_authority_allows_exact_observed_promotion(self):
        self.prepare_promoted_acceptance()
        self.item["plan"]["promotion_authorized"] = True
        self.assertEqual(self.errors(), [])


if __name__ == "__main__":
    unittest.main()
