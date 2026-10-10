"""Read-only Jira approval and QA receipt checks; no network or Jira writes."""
import hashlib
import json
import re
from pathlib import PurePosixPath
from urllib.parse import urlparse

BOARD_COLUMNS = ["Archive", "Backlog", "To Do", "In Progress", "Blocked", "QA", "Done"]
ISSUE_REF = re.compile(r"^([A-Z][A-Z0-9_]*-[1-9][0-9]*)@([1-9][0-9]*)$")
SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
ACTIVE = {"ready", "running", "review", "verified", "integrating"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_for(root, value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    actual = (root / value).resolve()
    return actual if actual.is_relative_to(root.resolve()) and actual.is_file() else None


def plan_ref(item):
    plan = item.get("plan") or {}
    return f"{plan.get('id')}@{plan.get('revision')}"


def subject_for(key, item, registry):
    subject = {"kind": "epic" if item.get("item_type") == "epic" else "candidate",
               "issue_key": key, "requirements_digest": item.get("requirements_digest"),
               "plan_ref": plan_ref(item), "completion_target": item.get("completion_target")}
    if subject["kind"] == "epic":
        subject["children"] = [
            {"issue_key": child, "acceptance_ref": (registry["work_items"][child].get("final_acceptance") or {}).get("source_ref"),
             "subject_digest": (registry["work_items"][child].get("final_acceptance") or {}).get("subject_digest")}
            for child in sorted(item.get("child_keys", [])) if child in registry["work_items"]]
    else:
        subject["candidate_commit"] = item.get("candidate_commit")
        if item.get("completion_target") == "promoted":
            subject["target_base_commit"] = item.get("target_base_commit")
    return subject


def receipt_errors(receipt, decision, expected, humans):
    if not isinstance(receipt, dict) or receipt.get("decision") != decision:
        return ["missing explicit decision"]
    errors = []
    if receipt.get("author_account_id") not in humans:
        errors.append("decision must come from a configured human account")
    if not re.fullmatch(r"jira-comment:[0-9]+", str(receipt.get("source_ref", ""))):
        errors.append("missing actual Jira comment receipt")
    if any(receipt.get(field) != value for field, value in expected.items()):
        errors.append("decision is bound to stale requirements, plan, or QA evidence")
    return errors


def checks(root, registry, user_authorities=()):
    errors = []
    add = errors.append
    config = registry.get("jira")
    items = registry.get("work_items")
    if not isinstance(config, dict) or not isinstance(items, dict):
        return ["jira and work_items must be objects"]
    if config.get("board_columns") != BOARD_COLUMNS:
        add("Jira column order must be Archive, Backlog, To Do, In Progress, Blocked, QA, Done")
    if config.get("sync_mode") != "session_boundaries" or "poll_interval_seconds" in config:
        add("Jira requires session-boundary sync without periodic polling configuration")
    if config.get("sync_triggers") != ["session_start", "milestone", "inactivity"]:
        add("Jira sync triggers must be session_start, milestone, inactivity only")
    timeout = config.get("inactivity_timeout_seconds")
    if type(timeout) is not int or not 7200 <= timeout <= 10800:
        add("Jira inactivity timeout must be between two and three hours")
    if type(config.get("enabled")) is not bool:
        add("jira.enabled must be boolean")
    humans = config.get("user_account_ids", [])
    if not isinstance(humans, list) or not all(isinstance(x, str) and x for x in humans):
        add("Jira human account IDs must be a string array")
        humans = []
    if config.get("enabled"):
        site = urlparse(str(config.get("site_url", "")))
        if site.scheme != "https" or not site.netloc or site.username or site.password:
            add("Jira needs an actual HTTPS site URL without credentials")
        if not config.get("project_keys") or not humans or not config.get("master_account_id"):
            add("Jira needs projects, human account IDs, and a distinct Master account")
        if config.get("master_account_id") in humans:
            add("Jira Master account cannot be a human approval account")
        statuses = config.get("status_ids", {})
        if not isinstance(statuses, dict) or set(statuses) != set(BOARD_COLUMNS) or not all(isinstance(x, str) and x.isdigit() for x in statuses.values()) or len(set(statuses.values())) != 7:
            add("Jira needs seven distinct actual status IDs matching the columns")
    elif items:
        add("Jira work receipts require enabled, confirmed Jira configuration")
    tasks = registry.get("tasks", {})
    agents = registry.get("agents", {})
    profiles = registry.get("verification_profiles", {})
    for key, item in items.items():
        if not isinstance(item, dict) or not re.fullmatch(r"[A-Z][A-Z0-9_]*-[1-9][0-9]*", key):
            add(f"invalid Jira work item: {key}")
            continue
        status = item.get("board_status")
        if status not in BOARD_COLUMNS:
            add(f"{key}: invalid board status")
        if not file_for(root, item.get("file")):
            add(f"{key}: missing owned work-item record")
        if status == "Archive":
            continue
        planning = status == "Backlog" or status == "Blocked" and item.get("resume_status") == "Backlog"
        goal_unknown = planning and item.get("completion_target") is None
        if item.get("item_type") not in {"delivery", "epic"} or not goal_unknown and item.get("completion_target") not in {"local", "promoted"}:
            add(f"{key}: invalid item type or completion target")
        if type(item.get("requirements_revision")) is not int or item["requirements_revision"] < 1:
            add(f"{key}: requirements_revision must be positive")
        source = file_for(root, item.get("requirements_file"))
        try:
            if not source or digest(json.loads(source.read_text(encoding="utf-8"))) != item.get("requirements_digest"):
                add(f"{key}: requirements digest does not match the retained snapshot")
        except (OSError, ValueError):
            add(f"{key}: cannot inspect requirements snapshot")
        plan = item.get("plan")
        needs_approval = status in {"To Do", "In Progress", "QA", "Done"}
        if plan is not None:
            if not isinstance(plan, dict):
                add(f"{key}: plan must be an object")
                plan = None
            else:
                path = file_for(root, plan.get("file"))
                identity = plan.get("id")
                if not re.fullmatch(r"PLAN-[0-9]{4,}", str(identity)) or type(plan.get("revision")) is not int or plan["revision"] < 1:
                    add(f"{key}: invalid plan identity/revision")
                if not path or not re.search(rf"^Plan ID: {re.escape(str(identity))}\s*$", path.read_text(encoding="utf-8"), re.M) or not re.search(rf"^Revision: {plan.get('revision')}\s*$", path.read_text(encoding="utf-8"), re.M):
                    add(f"{key}: missing or mismatched plan file")
        if needs_approval:
            if not plan or plan.get("requirements_revision") != item.get("requirements_revision") or plan.get("requirements_digest") != item.get("requirements_digest"):
                add(f"{key}: plan approval needs current requirements")
            else:
                for error in receipt_errors(plan.get("approval"), "approved", {"plan_ref": plan_ref(item), "requirements_digest": item.get("requirements_digest")}, humans):
                    add(f"{key}: plan approval: {error}")
        execution = item.get("execution_tasks", [])
        if not isinstance(execution, list) or not all(isinstance(x, str) and x in tasks for x in execution):
            add(f"{key}: execution_tasks must name registered tasks")
            execution = []
        if needs_approval:
            for task_id in execution:
                task = tasks[task_id]
                if task.get("request_ref") != f"{key}@{item.get('requirements_revision')}" or task.get("plan_ref") != plan_ref(item) or task.get("requirements_digest") != item.get("requirements_digest"):
                    add(f"{key}: execution task binding is stale or belongs to another request: {task_id}")
        if status == "Blocked" and item.get("resume_status") not in {"Backlog", "To Do", "In Progress", "QA"}:
            add(f"{key}: Blocked needs its previous resume_status")
        if item.get("item_type") == "epic":
            children = item.get("child_keys", [])
            if not isinstance(children, list) or not all(isinstance(x, str) and x in items and x != key for x in children):
                add(f"{key}: epic needs valid child_keys")
                children = []
            known = sorted(k for k, child in items.items() if isinstance(child, dict) and child.get("parent_key") == key)
            if sorted(children) != known:
                add(f"{key}: epic child set does not match registered hierarchy")
            if status in {"QA", "Done"} and (not children or any(items[c].get("board_status") != "Done" for c in children)):
                add(f"{key}: epic QA/Done requires accepted Done children")
        elif status in {"QA", "Done"} and not SHA.fullmatch(str(item.get("candidate_commit", ""))):
            add(f"{key}: QA needs an exact immutable candidate_commit")
        if status in {"QA", "Done"} and item.get("item_type") != "epic" and item.get("completion_target") == "promoted" and not SHA.fullmatch(str(item.get("target_base_commit", ""))):
            add(f"{key}: promoted QA needs exact target_base_commit")
        qa_id = item.get("qa_task_id")
        qa = tasks.get(qa_id) if isinstance(qa_id, str) else None
        if status in {"QA", "Done"} and not qa:
            add(f"{key}: QA needs an independent registered QA task")
        if qa:
            qa_agent = qa.get("assignee")
            if qa.get("request_ref") != f"{key}@{item.get('requirements_revision')}" or qa.get("plan_ref") != plan_ref(item) or qa.get("requirements_digest") != item.get("requirements_digest"):
                add(f"{key}: QA task request or approved plan binding is stale")
            if qa.get("kind") != "qa" or agents.get(qa_agent, {}).get("specialization") != "qa" or any(tasks[x].get("assignee") == qa_agent for x in execution):
                add(f"{key}: QA must be independent from implementation and integration")
            if qa.get("write_paths") or qa.get("merge_sources") or agents.get(qa_agent, {}).get("owns"):
                add(f"{key}: QA source write/merge authority must be empty")
            if any(not profiles.get(p, {}).get("master_safe") for p in qa.get("verification_profiles", [])):
                add(f"{key}: QA profiles must preserve source and production data")
            expected_subject = subject_for(key, item, registry)
            if qa.get("qa_subject") != expected_subject or qa.get("qa_subject_digest") != digest(expected_subject):
                add(f"{key}: QA subject is stale or incorrectly bound")
            report = qa.get("qa_report")
            if report is not None and not isinstance(report, dict):
                add(f"{key}: QA report receipt must be an object")
                report = None
            if report:
                path = file_for(root, report.get("file"))
                if not re.fullmatch(r"QA-[0-9]{4,}", str(report.get("id"))) or type(report.get("revision")) is not int or report["revision"] < 1:
                    add(f"{key}: invalid QA report identity/revision")
                if not path or not str(report.get("file", "")).startswith(f"agents/{qa_agent}/") or not re.search(rf"^Report ID: {re.escape(str(report.get('id')))}\s*$", path.read_text(encoding="utf-8"), re.M) or not re.search(rf"^Revision: {report.get('revision')}\s*$", path.read_text(encoding="utf-8"), re.M):
                    add(f"{key}: missing or mismatched QA-owned report")
                if report.get("subject_digest") != qa.get("qa_subject_digest") or report.get("verdict") not in {"pass", "fail", "blocked"}:
                    add(f"{key}: QA report is stale or has an invalid verdict")
            if status == "Done":
                if not report or report.get("verdict") != "pass" or qa.get("state") != "done":
                    add(f"{key}: Done requires passing QA reviewed by Master")
                report_ref = f"{(report or {}).get('id')}@{(report or {}).get('revision')}"
                expected = {"plan_ref": plan_ref(item), "requirements_digest": item.get("requirements_digest"),
                            "qa_report_ref": report_ref, "subject_digest": qa.get("qa_subject_digest")}
                for error in receipt_errors(item.get("final_acceptance"), "accepted", expected, humans):
                    add(f"{key}: final user acceptance: {error}")
                if any(tasks[x].get("state") != "done" for x in execution):
                    add(f"{key}: Done requires completed execution evidence")
                if item.get("item_type") != "epic" and item.get("completion_target") == "promoted":
                    authority = item.get("promotion_authority")
                    approved = plan and plan.get("promotion_authorized") is True and authority == (plan.get("approval") or {}).get("source_ref")
                    if not authority or not (authority in user_authorities or approved):
                        add(f"{key}: Done needs explicit current promotion authority")
                    if item.get("promoted_commit") != item.get("candidate_commit"):
                        add(f"{key}: Done requires observed exact promotion")
    report_allocations = {}
    for task_id, task in tasks.items():
        if not isinstance(task, dict):
            continue
        if task.get("kind") == "qa":
            allocated = task.get("qa_report_ref")
            if not re.fullmatch(r"QA-[0-9]{4,}@[1-9][0-9]*", str(allocated)):
                if task.get("state") != "draft":
                    add(f"{task_id}: QA needs a Master-allocated report identity/revision")
            else:
                if allocated in report_allocations:
                    add(f"{task_id}: report revision already allocated to {report_allocations[allocated]}")
                report_allocations[allocated] = task_id
                report = task.get("qa_report")
                if isinstance(report, dict) and allocated != f"{report.get('id')}@{report.get('revision')}":
                    add(f"{task_id}: submitted QA differs from allocated report identity/revision")
        if task.get("state") not in ACTIVE:
            continue
        source = ISSUE_REF.fullmatch(str(task.get("request_ref", "")))
        if not source:
            add(f"{task_id}: execution requires an approved Jira source work item")
            continue
        key, revision = source.groups()
        item = items.get(key)
        if not item:
            add(f"{task_id}: execution requires an approved Jira source work item")
            continue
        if item.get("board_status") not in {"To Do", "In Progress", "QA"}:
            add(f"{task_id}: cannot execute from {item.get('board_status')}")
        if int(revision) != item.get("requirements_revision") or task.get("requirements_digest") != item.get("requirements_digest") or task.get("plan_ref") != plan_ref(item):
            add(f"{task_id}: stale Jira requirements or approved plan binding")
        if task.get("kind") == "qa":
            if item.get("qa_task_id") != task_id or item.get("board_status") != "QA":
                add(f"{task_id}: QA task must be named by the item in QA")
        elif task_id not in item.get("execution_tasks", []):
            add(f"{task_id}: execution task is not named by its Jira item")
    return sorted(set(errors))
