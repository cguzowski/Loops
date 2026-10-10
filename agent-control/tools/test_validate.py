"""Exercise protocol gates against disposable control folders and real Git diffs.

Run: python -B -m unittest discover -s <CONTROL_ROOT>/tools -p test_validate.py -v
"""
import copy
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("foundation_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def run_git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def empty_registry():
    """Keep test assignments independent of a deployed registry's live work."""
    deployed = json.loads((HERE.parent / "REGISTRY.json").read_text())
    return {"schema_version": 2, "revision": 1,
            "policy_revision": deployed["policy_revision"], "setup_complete": False,
            "protected_source_paths": ["AGENTS.md", "AGENTS.override.md", ".codex/"],
            "agents": {}, "tasks": {}, "contracts": {}, "verification_profiles": {},
            "jira": copy.deepcopy(deployed["jira"]), "work_items": {}}


def build_fixture(target):
    """Create an isolated, fictional catalog project for protocol verification."""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    control = target / "agent-control"
    shutil.copytree(HERE.parent, control,
                    ignore=shutil.ignore_patterns("__pycache__", "agents", "tasks", "contracts", "archive"))
    for name in ("agents", "tasks", "contracts", "archive/master", "work-items", "plans"):
        (control / name).mkdir(parents=True, exist_ok=True)
    code = target / "code"
    code.mkdir()
    contents = {
        "domains/catalog/service.py": "def normalize_label(value):\n    return value.strip()\n",
        "platform/shared/helper.py": "def display_label(value):\n    return value.strip()\n",
        "tests/catalog/test_labels.py": "import unittest\nfrom domains.catalog.service import normalize_label\n\nclass Labels(unittest.TestCase):\n    def test_trimming(self):\n        self.assertEqual(normalize_label(' desk '), 'desk')\n",
        "AGENTS.md": (HERE.parent.parent / "AGENTS.md").read_text() if (HERE.parent.parent / "AGENTS.md").exists() else "# Follow the shared agent protocol\n"
    }
    for name, content in contents.items():
        path = code / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    run_git(code, "init", "-b", "main")
    run_git(code, "config", "user.name", "Foundation Verification")
    run_git(code, "config", "user.email", "verification@example.invalid")
    run_git(code, "add", ".")
    run_git(code, "commit", "-m", "Disposable fixture baseline")
    base = run_git(code, "rev-parse", "HEAD")
    branch = "agent/catalog/TASK-0001"
    run_git(code, "checkout", "-b", branch)
    registry = empty_registry()
    registry["setup_complete"] = True
    registry["jira"].update(enabled=True, site_url="https://fixture.atlassian.net", project_keys=["DEMO"],
                            user_account_ids=["fixture-owner"], master_account_id="fixture-master",
                            status_ids={name: str(i+1) for i, name in enumerate(validator.workflow.BOARD_COLUMNS)})
    requirements = {"summary": "Canonical catalog labels", "acceptance": ["Trim and lowercase", "Blank raises ValueError"]}
    requirement_digest = validator.workflow.digest(requirements)
    (control / "work-items/DEMO-1-r1.json").write_text(json.dumps(requirements))
    (control / "work-items/DEMO-1.md").write_text("# Fictional Jira intake\n")
    (control / "plans/PLAN-0001-v1.md").write_text("Plan ID: PLAN-0001\nRevision: 1\n")
    registry["work_items"]["DEMO-1"] = {
        "file": "work-items/DEMO-1.md", "item_type": "delivery", "parent_key": None, "board_status": "To Do",
        "requirements_revision": 1, "requirements_file": "work-items/DEMO-1-r1.json", "requirements_digest": requirement_digest,
        "plan": {"id": "PLAN-0001", "revision": 1, "file": "plans/PLAN-0001-v1.md", "requirements_revision": 1,
                 "requirements_digest": requirement_digest, "approval": {"decision": "approved", "author_account_id": "fixture-owner",
                 "source_ref": "jira-comment:100", "plan_ref": "PLAN-0001@1", "requirements_digest": requirement_digest}},
        "execution_tasks": ["TASK-0001"], "completion_target": "local", "candidate_commit": None,
        "qa_task_id": None, "final_acceptance": None}
    agents = {
        "catalog-agent": ("implementation", ["catalog"], ["domain-service"], ["domains/catalog/", "tests/catalog/"]),
        "platform-agent": ("implementation", [], ["shared-formatting"], ["platform/shared/"]),
        "integration-agent": ("integration", [], ["repository-integration"], []),
        "qa-agent": ("qa", [], ["quality"], [])
    }
    for agent_id, (specialization, domains, layers, owns) in agents.items():
        record = control / "agents" / agent_id / "AGENT.md"
        record.parent.mkdir(parents=True, exist_ok=True)
        template = (control / "templates/SUBAGENT.md").read_text().replace("<AGENT-ID>", agent_id)
        template = template.replace("<stable lowercase ID>", agent_id).replace("<registry charter_revision>", "1")
        record.write_text(template)
        registry["agents"][agent_id] = {"record": f"agents/{agent_id}/AGENT.md", "charter_revision": 1, "specialization": specialization, "domains": domains, "layers": layers, "owns": owns}
    registry["verification_profiles"] = {
        "catalog-unit": {"commands": ["python -B -m unittest discover -s tests/catalog -v"], "source": f"tests/catalog/test_labels.py at {base}", "environment": "Disposable local fixture; no external services; bytecode disabled", "master_safe": True}
    }
    registry["tasks"]["TASK-0001"] = {
        "revision": 1, "policy_revision": registry["policy_revision"], "charter_revision": 1,
        "request_ref": "DEMO-1@1", "plan_ref": "PLAN-0001@1", "requirements_digest": requirement_digest,
        "kind": "implementation", "assignee": "catalog-agent",
        "completion_target": "promoted",
        "file": "tasks/TASK-0001.md", "state": "ready", "base_commit": base,
        "branch": branch, "worktree": str(code.resolve()),
        "write_paths": ["domains/catalog/", "tests/catalog/"], "contracts": [],
        "depends_on": [], "verification_profiles": ["catalog-unit"], "candidate_commit": None,
        "merge_sources": [], "governance_approval": None, "promotion_authority": None
    }
    (control / "tasks/TASK-0001.md").write_text(
        "# TASK-0001 — Canonical catalog labels\n\nTask ID: TASK-0001\nRevision: 1\n\n"
        "Writer: MasterAgent. Envelope: REGISTRY.json. Source request: DEMO-1@1.\n\n"
        "## Required outcome\nUse the existing normalize_label function. Trim leading/trailing whitespace and lowercase labels. "
        "A whitespace-only label must raise ValueError. No other shared formatting changes are requested.\n\n"
        "## Acceptance criteria\n- AC-1: normalize_label(' Desk ') returns 'desk'.\n"
        "- AC-2: normalize_label('   ') raises ValueError.\n"
        "- AC-3: Existing trimming behavior for lowercase labels remains supported.\n\n"
        "Verification profile: catalog-unit. Implement using TDD and report actual red/green results. "
        "Read actual source and preserve existing tests. Source paths and write authority are in the registry. "
        "Submit an immutable candidate SHA and your owned handoff. Do not merge or change shared code.\n"
    )
    user = control / "communication/USER.md"
    user.write_text(user.read_text() + "\n### RQ-0002 — Canonical catalog labels\n\n- Revision: 1\n"
                    "- Requested outcome: Trim and lowercase catalog labels; whitespace-only input raises ValueError.\n"
                    "- Scope: Existing catalog service and its tests in this disposable local project.\n"
                    "- Integration authority: Local candidate preparation only; no target promotion or remote actions.\n")
    (control / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n")
    return control, code, registry


class ProtocolGates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.control, self.code, self.registry = build_fixture(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def check(self):
        return validator.checks(self.control, self.registry, ready=True)

    def second_task(self, state="ready"):
        task = copy.deepcopy(self.registry["tasks"]["TASK-0001"])
        task.update(assignee="platform-agent", file="tasks/TASK-0002.md", state=state,
                    branch="agent/platform/TASK-0002", worktree=str(self.code.parent / "other-code"),
                    write_paths=["platform/shared/"])
        self.registry["tasks"]["TASK-0002"] = task
        self.registry["work_items"]["DEMO-1"]["execution_tasks"].append("TASK-0002")
        (self.control / task["file"]).write_text("# Platform task\nTask ID: TASK-0002\nRevision: 1\n")
        return task

    def test_valid_disjoint_tasks(self):
        self.second_task()
        self.assertEqual(self.check(), [])

    def test_unconfigured_starter_is_not_ready(self):
        starter = empty_registry()
        self.assertEqual(validator.checks(HERE.parent, starter), [])
        self.assertTrue(validator.checks(HERE.parent, starter, ready=True))

    def test_overlapping_domain_and_layer_ownership_is_rejected(self):
        self.registry["agents"]["platform-agent"]["owns"] = ["domains/"]
        self.assertTrue(any("ownership overlap" in e for e in self.check()))

    def test_case_only_owner_overlap_is_rejected_for_windows_portability(self):
        self.registry["agents"]["platform-agent"]["owns"] = ["Domains/Catalog/"]
        self.assertTrue(any("ownership overlap" in e for e in self.check()))

    def test_live_worktree_requires_an_absolute_path(self):
        self.registry["tasks"]["TASK-0001"]["worktree"] = "relative/catalog"
        self.assertTrue(any("absolute" in e for e in self.check()))

    def test_parallel_tasks_for_one_record_are_rejected(self):
        other = self.second_task()
        other.update(assignee="catalog-agent", write_paths=["tests/catalog/"])
        self.assertTrue(any("already reserved" in e for e in self.check()))
        self.assertTrue(any("reservation overlap" in e for e in self.check()))

    def test_dependency_cycle_is_rejected(self):
        other = self.second_task(state="draft")
        self.registry["tasks"]["TASK-0001"]["depends_on"] = [{"task_id": "TASK-0002", "required_state": "done"}]
        other["depends_on"] = [{"task_id": "TASK-0001", "required_state": "done"}]
        self.assertTrue(any("dependency cycle" in e for e in self.check()))

    def test_outdated_task_markdown_is_rejected(self):
        self.registry["tasks"]["TASK-0001"]["revision"] = 2
        self.assertTrue(any("Markdown identity/revision" in e for e in self.check()))

    def test_contract_needs_both_owner_acknowledgements(self):
        (self.control / "contracts/CON-0001-v1.md").write_text("Contract ID: CON-0001\nRevision: 1\n")
        self.registry["contracts"]["CON-0001@1"] = {"file": "contracts/CON-0001-v1.md", "state": "agreed", "producer": "catalog-agent", "consumer": "platform-agent", "acknowledgements": {"catalog-agent": "agents/catalog-agent/AGENT.md#boundary"}}
        self.assertTrue(any("both acknowledgement" in e for e in self.check()))

    def test_out_of_scope_untracked_file_is_rejected(self):
        (self.code / "platform/shared/new.py").write_text("value = 1\n")
        errors, paths = validator.audit(self.control, self.registry, "TASK-0001", "catalog-agent", self.code, working=True)
        self.assertIn("platform/shared/new.py", paths)
        self.assertTrue(any("out-of-scope" in e for e in errors))

    def test_rename_checks_both_paths(self):
        run_git(self.code, "mv", "domains/catalog/service.py", "platform/shared/moved.py")
        errors, paths = validator.audit(self.control, self.registry, "TASK-0001", "catalog-agent", self.code, working=True)
        self.assertIn("domains/catalog/service.py", paths)
        self.assertIn("platform/shared/moved.py", paths)
        self.assertTrue(any("out-of-scope" in e for e in errors))

    def test_in_scope_dirty_change_is_allowed(self):
        (self.code / "domains/catalog/service.py").write_text("def normalize_label(value):\n    return value.strip().lower()\n")
        errors, paths = validator.audit(self.control, self.registry, "TASK-0001", "catalog-agent", self.code, working=True)
        self.assertEqual(errors, [])
        self.assertEqual(paths, ["domains/catalog/service.py"])

    def test_unapproved_instruction_change_is_rejected(self):
        self.registry["agents"]["catalog-agent"]["owns"].append("AGENTS.md")
        self.registry["tasks"]["TASK-0001"]["write_paths"].append("AGENTS.md")
        (self.code / "AGENTS.md").write_text("# Changed instructions\n")
        self.assertTrue(any("governance scope" in e for e in self.check()))

    def test_integration_accepts_only_frozen_exact_source(self):
        source = self.registry["tasks"]["TASK-0001"]
        source.update(state="verified", candidate_commit=source["base_commit"])
        integration = self.second_task()
        integration.update(kind="integration", assignee="integration-agent", write_paths=[],
                           merge_sources=[{"task_id": "TASK-0001", "commit": source["candidate_commit"]}])
        self.assertEqual(self.check(), [])
        integration["merge_sources"][0]["commit"] = "f" * 40
        self.assertTrue(any("stale or invalid source" in e for e in self.check()))

    def test_completed_task_keeps_its_historical_ownership_receipt(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(state="done", completion_target="local", candidate_commit=task["base_commit"],
                    completion_evidence="Master verdict for the exact local candidate")
        self.registry["agents"]["catalog-agent"]["owns"] = []
        self.registry["agents"]["platform-agent"]["owns"].extend(["domains/catalog/", "tests/catalog/"])
        self.assertEqual(self.check(), [])

    def test_real_combined_candidate_preserves_exact_source_commits(self):
        source = self.registry["tasks"]["TASK-0001"]
        base = source["base_commit"]
        (self.code / "domains/catalog/service.py").write_text("def normalize_label(value):\n    return value.strip().lower()\n")
        run_git(self.code, "add", "domains/catalog/service.py")
        run_git(self.code, "commit", "-m", "Catalog candidate")
        catalog_sha = run_git(self.code, "rev-parse", "HEAD")
        source.update(state="verified", candidate_commit=catalog_sha)
        second = self.second_task(state="verified")
        run_git(self.code, "checkout", "-b", second["branch"], base)
        (self.code / "platform/shared/helper.py").write_text("def display_label(value):\n    return value.strip().lower()\n")
        run_git(self.code, "add", "platform/shared/helper.py")
        run_git(self.code, "commit", "-m", "Shared candidate")
        shared_sha = run_git(self.code, "rev-parse", "HEAD")
        second["candidate_commit"] = shared_sha
        integration = copy.deepcopy(second)
        integration.update(assignee="integration-agent", kind="integration", state="ready",
                           branch="agent/integration/TASK-0003", worktree=str(self.code.parent / "integration-code"),
                           file="tasks/TASK-0003.md", write_paths=[], candidate_commit=None,
                           merge_sources=[{"task_id": "TASK-0001", "commit": catalog_sha}, {"task_id": "TASK-0002", "commit": shared_sha}])
        self.registry["tasks"]["TASK-0003"] = integration
        self.registry["work_items"]["DEMO-1"]["execution_tasks"].append("TASK-0003")
        (self.control / integration["file"]).write_text("Task ID: TASK-0003\nRevision: 1\n")
        run_git(self.code, "checkout", "-b", integration["branch"], base)
        run_git(self.code, "merge", "--no-ff", catalog_sha, "-m", "Include catalog candidate")
        run_git(self.code, "merge", "--no-ff", shared_sha, "-m", "Include shared candidate")
        candidate = run_git(self.code, "rev-parse", "HEAD")
        errors, paths = validator.audit(self.control, self.registry, "TASK-0003", "integration-agent", self.code, head=candidate)
        self.assertEqual(errors, [])
        self.assertEqual(paths, ["domains/catalog/service.py", "platform/shared/helper.py"])
        errors, _ = validator.audit(self.control, self.registry, "TASK-0003", "integration-agent", self.code, head=base)
        self.assertTrue(any("does not preserve named source" in e for e in errors))

    def test_workspace_setup_has_no_source_write_or_merge_authority(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(kind="workspace", assignee="integration-agent", completion_target="local",
                    write_paths=[], workspace_outputs=[{"branch": "agent/new/TASK-0002", "worktree": str(self.code.parent / "new-worktree"), "base_commit": task["base_commit"]}])
        self.assertEqual(self.check(), [])
        task["write_paths"] = ["domains/catalog/"]
        self.assertTrue(any("workspace" in e for e in self.check()))

    def test_local_only_completion_releases_reservation_without_promotion(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(state="done", completion_target="local", candidate_commit=task["base_commit"],
                    completion_evidence="MASTER.md local acceptance verdict")
        self.assertEqual(self.check(), [])
        other = self.second_task()
        other.update(kind="integration", assignee="integration-agent", completion_target="local", write_paths=[],
                     merge_sources=[{"task_id": "TASK-0001", "commit": task["candidate_commit"]}])
        self.assertEqual(self.check(), [])

    def test_workspace_completion_does_not_require_an_application_commit(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(kind="workspace", assignee="integration-agent", completion_target="local", state="done",
                    write_paths=[], candidate_commit=None,
                    workspace_outputs=[{"branch": "agent/new/TASK-0002", "worktree": str(self.code.parent / "new-worktree"), "base_commit": task["base_commit"]}],
                    completion_evidence="MASTER.md observed workspace/branch/base receipt")
        self.assertEqual(self.check(), [])

    def test_workspace_task_rejects_source_changes_in_actual_git_diff(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(kind="workspace", assignee="integration-agent", completion_target="local",
                    write_paths=[], workspace_outputs=[{"branch": "agent/new/TASK-0002", "worktree": str(self.code.parent / "new-worktree"), "base_commit": task["base_commit"]}])
        (self.code / "domains/catalog/service.py").write_text("def normalize_label(value):\n    return value.strip().lower()\n")
        errors, _ = validator.audit(self.control, self.registry, "TASK-0001", "integration-agent", self.code, working=True)
        self.assertTrue(any("out-of-scope changed path" in e for e in errors))

    def test_workspace_outputs_cannot_use_another_active_worktree(self):
        other = self.second_task()
        task = self.registry["tasks"]["TASK-0001"]
        task.update(kind="workspace", assignee="integration-agent", completion_target="local",
                    write_paths=[], workspace_outputs=[{"branch": other["branch"], "worktree": other["worktree"], "base_commit": task["base_commit"]}])
        self.assertTrue(any("already reserved" in e for e in self.check()))

    def test_promoted_completion_cannot_be_claimed_without_promotion_receipt(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(state="done", candidate_commit=task["base_commit"],
                    completion_evidence="MASTER.md acceptance verdict")
        self.assertTrue(any("promoted completion needs authority" in e for e in self.check()))

    def prepare_qa_task(self):
        record = self.control / "agents/qa-agent/AGENT.md"
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("# Independent QA record\n")
        self.registry["agents"]["qa-agent"] = {
            "record": "agents/qa-agent/AGENT.md", "charter_revision": 1,
            "specialization": "qa", "domains": [], "layers": ["quality"], "owns": []}
        task = self.registry["tasks"]["TASK-0001"]
        task.update(kind="qa", assignee="qa-agent", completion_target="local", write_paths=[], qa_report_ref="QA-0001@1")
        item = self.registry["work_items"]["DEMO-1"]
        item.update(board_status="QA", candidate_commit=task["base_commit"], execution_tasks=[], qa_task_id="TASK-0001")
        task["qa_subject"] = validator.workflow.subject_for("DEMO-1", item, self.registry)
        task["qa_subject_digest"] = validator.workflow.digest(task["qa_subject"])
        return task

    def test_qa_accepts_exact_frozen_checkout_without_source_changes(self):
        self.prepare_qa_task()
        errors, paths = validator.audit(self.control, self.registry, "TASK-0001", "qa-agent", self.code, working=True)
        self.assertEqual((errors, paths), ([], []))

    def test_qa_rejects_source_edits_in_real_git_worktree(self):
        self.prepare_qa_task()
        (self.code / "domains/catalog/service.py").write_text("def normalize_label(value):\n    return value.strip().lower()\n")
        errors, paths = validator.audit(self.control, self.registry, "TASK-0001", "qa-agent", self.code, working=True)
        self.assertIn("domains/catalog/service.py", paths)
        self.assertTrue(any("out-of-scope changed path" in error for error in errors))

    def test_ready_setup_requires_an_independent_qa_role(self):
        del self.registry["agents"]["qa-agent"]
        self.assertTrue(any("QA specialist" in error for error in self.check()))

    def test_windows_aliases_cannot_reserve_one_worktree_twice(self):
        other = self.second_task()
        self.registry["tasks"]["TASK-0001"]["worktree"] = "C:/Dev/Shared-Worktree"
        other["worktree"] = "c:\\dev\\shared-worktree"
        self.assertTrue(any("already reserved" in error for error in self.check()))

    def test_paused_old_request_does_not_block_independent_work(self):
        other = self.second_task()
        item = copy.deepcopy(self.registry["work_items"]["DEMO-1"])
        item["file"] = "work-items/DEMO-2.md"
        (self.control / item["file"]).write_text("# Independent intake\n")
        item["plan"].update(id="PLAN-0002", file="plans/PLAN-0002-v1.md")
        item["plan"]["approval"]["plan_ref"] = "PLAN-0002@1"
        (self.control / item["plan"]["file"]).write_text("Plan ID: PLAN-0002\nRevision: 1\n")
        item["execution_tasks"] = ["TASK-0002"]
        self.registry["work_items"]["DEMO-2"] = item
        other.update(request_ref="DEMO-2@1", plan_ref="PLAN-0002@1")
        run_git(self.code, "worktree", "add", "-b", other["branch"], other["worktree"], other["base_commit"])
        changed = {"summary": "Changed catalog intent", "acceptance": ["Preserve case"]}
        path = "work-items/DEMO-1-r2.json"
        (self.control / path).write_text(json.dumps(changed))
        original = self.registry["work_items"]["DEMO-1"]
        original.update(board_status="Blocked", resume_status="In Progress", plan=None,
                        requirements_revision=2, requirements_file=path,
                        requirements_digest=validator.workflow.digest(changed), execution_tasks=["TASK-0001"])
        paused = self.registry["tasks"]["TASK-0001"]
        paused.update(state="blocked", policy_revision=1, charter_revision=1)
        self.assertEqual(self.check(), [])
        errors, _ = validator.audit(self.control, self.registry, "TASK-0002", "platform-agent", Path(other["worktree"]), working=True)
        self.assertEqual(errors, [])
        paused["state"] = "ready"
        self.assertTrue(any("stale USER or Jira request" in error for error in self.check()))

    def test_historical_promotion_receipt_survives_a_later_replan(self):
        task = self.registry["tasks"]["TASK-0001"]
        task.update(state="done", candidate_commit=task["base_commit"], promoted_commit=task["base_commit"],
                    promotion_authority="jira-comment:100", completion_evidence="Prior observed promotion receipt")
        self.registry["work_items"]["DEMO-1"].update(board_status="Backlog", plan=None, execution_tasks=[])
        self.assertEqual(self.check(), [])


if __name__ == "__main__":
    unittest.main()
