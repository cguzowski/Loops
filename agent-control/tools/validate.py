#!/usr/bin/env python3
"""Read-only structural and Git scope checks for the SaaS agent protocol.

Python 3.10+; standard library only. Does not run project commands or mutate Git.
This is an audit aid, not an authorization or sandbox boundary.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
import workflow

STATES = {"draft", "ready", "running", "blocked", "review", "verified", "integrating", "done", "cancelled"}
RESERVED = STATES - {"draft", "done", "cancelled"}
FROZEN = {"verified", "integrating", "done"}
SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
AGENT = re.compile(r"^[a-z][a-z0-9-]*$")
TASK = re.compile(r"^TASK-[0-9]{4,}$")
CONTRACT = re.compile(r"^CON-[0-9]{4,}@[1-9][0-9]*$")


def is_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def valid_scope(value):
    if not isinstance(value, str) or not value or value.startswith("/"):
        return False
    if any(c in value for c in "\\:*?[]{}\x00\n\r"):
        return False
    parts = value.rstrip("/").split("/")
    return all(p not in {"", ".", ".."} for p in parts)


def covers(scope, path):
    return scope == path or (scope.endswith("/") and path.startswith(scope))


def overlaps(left, right):
    # Conservatively reject case-only collisions for Windows portability.
    left, right = left.casefold(), right.casefold()
    return covers(left, right) or covers(right, left)


def local_file(root, value):
    if not valid_scope(value) or value.endswith("/"):
        return None
    resolved = (root / value).resolve()
    return resolved if resolved.is_relative_to(root.resolve()) and resolved.is_file() else None


def worktree_key(value):
    if not isinstance(value, str):
        return value
    if PureWindowsPath(value).is_absolute():
        return str(PureWindowsPath(value)).casefold()
    return str(Path(value).resolve()) if PurePosixPath(value).is_absolute() else value


def effective_paths(task, registry):
    if task.get("kind") in {"workspace", "qa"}:
        return []
    if task.get("kind") != "integration":
        return task.get("write_paths", [])
    paths = []
    for source in task.get("merge_sources", []):
        original = registry.get("tasks", {}).get(source.get("task_id"), {})
        paths.extend(original.get("write_paths", []))
    return sorted(set(paths))


def source_handoff(left_id, left, right_id, right):
    for integrator, source_id, original in ((left, right_id, right), (right, left_id, left)):
        if integrator.get("kind") == "integration" and original.get("state") in FROZEN:
            if any(s.get("task_id") == source_id for s in integrator.get("merge_sources", [])):
                return True
    return False


def request_revisions(text):
    found = {}
    for match in re.finditer(r"^### (RQ-[0-9]{4,})\b[^\n]*\n(.*?)(?=^### |\Z)", text, re.M | re.S):
        revision = re.search(r"^- Revision: ([1-9][0-9]*)\s*$", match.group(2), re.M)
        if revision:
            found[match.group(1)] = int(revision.group(1))
    return found


def checks(root, registry, ready=False):
    errors = []
    add = errors.append
    if registry.get("schema_version") != 2:
        add("schema_version must be 2; follow the version 1.1 migration guide")
    for field in ("revision", "policy_revision"):
        if type(registry.get(field)) is not int or registry[field] < 1:
            add(f"{field} must be a positive integer")
    if type(registry.get("setup_complete")) is not bool:
        add("setup_complete must be boolean")
    for field in ("agents", "tasks", "contracts", "verification_profiles", "jira", "work_items"):
        if not isinstance(registry.get(field), dict):
            add(f"{field} must be an object")
    if errors:
        return errors
    for name in ("POLICY.md", "INDEX.md", "PROJECT.md", "GLOSSARY.md", "DECISIONS.md", "JIRA_WORKFLOW.md", "communication/USER.md", "communication/MASTER.md"):
        if not local_file(root, name):
            add(f"missing live record: {name}")
    communication = root / "communication"
    if communication.is_dir():
        names = sorted(p.name for p in communication.glob("*.md"))
        if names != ["MASTER.md", "USER.md"]:
            add("communication must contain exactly MASTER.md and USER.md")
    policy = local_file(root, "POLICY.md")
    if policy:
        match = re.search(r"^Revision: ([0-9]+)\s*$", policy.read_text(encoding="utf-8"), re.M)
        if not match or int(match.group(1)) != registry["policy_revision"]:
            add("POLICY.md revision does not match registry policy_revision")
    user = local_file(root, "communication/USER.md")
    user_text = user.read_text(encoding="utf-8") if user else ""
    requests = request_revisions(user_text)
    user_authorities = {f"{key}@{revision}" for key, revision in requests.items()}
    requests.update({key: item.get("requirements_revision") for key, item in registry["work_items"].items() if isinstance(item, dict)})
    decisions = set(re.findall(r"^### (DEC-[0-9]{4,})\b", user_text, re.M))
    user_authorities.update(decisions)
    agents = registry["agents"]
    tasks = registry["tasks"]
    contracts = registry["contracts"]
    profiles = registry["verification_profiles"]
    if ready and not registry.get("setup_complete"):
        add("bootstrap incomplete: setup_complete is false")
    if ready and (not agents or not profiles):
        add("ready setup needs registered agents and actual verification profiles")
    if ready and not registry["jira"].get("enabled"):
        add("ready setup needs confirmed Jira configuration; bootstrap stays read-only")
    if ready and not any(isinstance(agent, dict) and agent.get("specialization") == "qa" for agent in agents.values()):
        add("ready setup needs an independent registered QA specialist")
    ownership = []
    for agent_id, agent in agents.items():
        if not AGENT.fullmatch(agent_id) or not isinstance(agent, dict):
            add(f"invalid agent entry: {agent_id}")
            continue
        if agent.get("record") != f"agents/{agent_id}/AGENT.md" or not local_file(root, agent.get("record")):
            add(f"{agent_id}: missing or incorrect owned agent record")
        if type(agent.get("charter_revision")) is not int or agent["charter_revision"] < 1:
            add(f"{agent_id}: invalid charter_revision")
        if agent.get("specialization") not in {"implementation", "integration", "tooling", "qa"}:
            add(f"{agent_id}: invalid specialization")
        if agent.get("specialization") == "qa" and agent.get("owns"):
            add(f"{agent_id}: QA agents do not own source write paths")
        for field in ("domains", "layers", "owns"):
            if not isinstance(agent.get(field), list) or not all(isinstance(x, str) for x in agent[field]):
                add(f"{agent_id}: {field} must be a string array")
        for scope in agent.get("owns", []) if isinstance(agent.get("owns"), list) else []:
            if not valid_scope(scope):
                add(f"{agent_id}: invalid ownership scope {scope!r}")
                continue
            for other_id, other_scope in ownership:
                if other_id != agent_id and overlaps(scope, other_scope):
                    add(f"ownership overlap: {agent_id}:{scope} and {other_id}:{other_scope}")
            ownership.append((agent_id, scope))
    for name, profile in profiles.items():
        if not isinstance(profile, dict):
            add(f"{name}: verification profile must be an object")
            continue
        commands = profile.get("commands")
        if not isinstance(commands, list) or not commands or not all(isinstance(c, str) and c.strip() and "<" not in c for c in commands):
            add(f"{name}: needs real command descriptions, not placeholders")
        for field in ("source", "environment"):
            if not isinstance(profile.get(field), str) or not profile[field].strip() or "<" in profile[field]:
                add(f"{name}: missing confirmed {field}")
        if type(profile.get("master_safe")) is not bool:
            add(f"{name}: master_safe must be boolean")
    for key, contract in contracts.items():
        if not CONTRACT.fullmatch(key) or not isinstance(contract, dict):
            add(f"invalid contract entry: {key}")
            continue
        path = local_file(root, contract.get("file"))
        if not path:
            add(f"{key}: missing contract file")
        else:
            contract_id, revision = key.split("@")
            content = path.read_text(encoding="utf-8")
            if not re.search(rf"^Contract ID: {re.escape(contract_id)}\s*$", content, re.M) or not re.search(rf"^Revision: {revision}\s*$", content, re.M):
                add(f"{key}: contract identity/revision mismatch")
        if contract.get("state") not in {"draft", "agreed", "retired"}:
            add(f"{key}: invalid contract state")
        for field in ("producer", "consumer"):
            if contract.get(field) not in agents:
                add(f"{key}: unregistered {field}")
        if contract.get("state") == "agreed":
            acknowledgements = contract.get("acknowledgements", {})
            if not isinstance(acknowledgements, dict) or any(not acknowledgements.get(contract.get(f)) for f in ("producer", "consumer")):
                add(f"{key}: agreed contract needs both acknowledgement references")
    reservations = []
    live_agents, branches, worktrees = {}, {}, {}
    graph = {}
    protected = registry.get("protected_source_paths", [])
    if not isinstance(protected, list) or not all(valid_scope(p) for p in protected):
        add("protected_source_paths must be valid relative file/prefix scopes")
        protected = []
    for task_id, task in tasks.items():
        if not TASK.fullmatch(task_id) or not isinstance(task, dict):
            add(f"invalid task entry: {task_id}")
            continue
        state = task.get("state")
        if state not in STATES:
            add(f"{task_id}: invalid state")
        if type(task.get("revision")) is not int or task["revision"] < 1:
            add(f"{task_id}: invalid revision")
        task_file = local_file(root, task.get("file"))
        if not task_file:
            add(f"{task_id}: missing task file")
        else:
            content = task_file.read_text(encoding="utf-8")
            if not re.search(rf"^Task ID: {re.escape(task_id)}\s*$", content, re.M) or not re.search(rf"^Revision: {task.get('revision')}\s*$", content, re.M):
                add(f"{task_id}: task Markdown identity/revision mismatch")
        assignee = task.get("assignee")
        if assignee not in agents:
            add(f"{task_id}: unregistered assignee")
        kind = task.get("kind")
        if kind not in {"implementation", "integration", "workspace", "qa"}:
            add(f"{task_id}: kind must be implementation, integration, workspace, or qa")
        goal = task.get("completion_target")
        if goal not in {"local", "promoted"}:
            add(f"{task_id}: completion_target must be local or promoted")
        for field in ("write_paths", "contracts", "depends_on", "verification_profiles", "merge_sources"):
            if not isinstance(task.get(field), list):
                add(f"{task_id}: {field} must be an array")
        if any(not isinstance(task.get(f), list) for f in ("write_paths", "contracts", "depends_on", "verification_profiles", "merge_sources")):
            continue
        for scope in task["write_paths"]:
            if not valid_scope(scope):
                add(f"{task_id}: invalid task scope {scope!r}")
            elif state not in {"blocked", "done", "cancelled"} and kind == "implementation" and not any(covers(own, scope) for own in agents.get(assignee, {}).get("owns", [])):
                add(f"{task_id}: scope outside {assignee}'s ownership: {scope}")
        if kind == "implementation" and task["merge_sources"]:
            add(f"{task_id}: implementation task cannot grant merge authority")
        if kind == "qa":
            if task["write_paths"] or task["merge_sources"] or agents.get(assignee, {}).get("specialization") != "qa" or goal != "local":
                add(f"{task_id}: QA needs QA specialist, local report milestone, and no source write/merge authority")
            if state in {"review", "verified", "done"} and not isinstance(task.get("qa_report"), dict):
                add(f"{task_id}: submitted QA needs an owned report receipt")
        outputs = task.get("workspace_outputs", [])
        if kind == "workspace":
            if task["write_paths"] or task["merge_sources"] or agents.get(assignee, {}).get("specialization") != "integration" or goal != "local":
                add(f"{task_id}: workspace needs integration specialist, local goal, and no source write/merge authority")
            if not isinstance(outputs, list) or (not outputs and state != "draft"):
                add(f"{task_id}: workspace needs declared workspace_outputs")
                outputs = []
            for output in outputs:
                if not isinstance(output, dict):
                    add(f"{task_id}: invalid workspace output")
                    continue
                branch, worktree = output.get("branch"), output.get("worktree")
                if not isinstance(branch, str) or not branch.strip() or "<" in branch:
                    add(f"{task_id}: workspace output needs an actual branch")
                if not isinstance(worktree, str) or "<" in worktree or not (PurePosixPath(worktree).is_absolute() or PureWindowsPath(worktree).is_absolute()):
                    add(f"{task_id}: workspace output needs an absolute worktree")
                if not is_sha(output.get("base_commit")):
                    add(f"{task_id}: workspace output needs a full actual base_commit SHA")
        if kind == "integration":
            if task["write_paths"] or agents.get(assignee, {}).get("specialization") != "integration":
                add(f"{task_id}: integration needs integration specialist and no new write_paths")
            if not task["merge_sources"] and state != "draft":
                add(f"{task_id}: integration needs verified source commits")
            seen_sources = set()
            for source in task["merge_sources"]:
                if not isinstance(source, dict):
                    add(f"{task_id}: invalid merge source")
                    continue
                original_id = source.get("task_id")
                original = tasks.get(original_id, {})
                if original_id in seen_sources or original_id == task_id or original.get("kind") != "implementation":
                    add(f"{task_id}: invalid/duplicate source task {original_id}")
                seen_sources.add(original_id)
                if state in RESERVED and original.get("state") not in FROZEN:
                    add(f"{task_id}: source {original_id} is not frozen verified work")
                if state != "draft" and (not is_sha(source.get("commit")) or source.get("commit") != original.get("candidate_commit")):
                    add(f"{task_id}: stale or invalid source candidate for {original_id}")
        request = re.fullmatch(r"(RQ-[0-9]{4,}|[A-Z][A-Z0-9_]*-[1-9][0-9]*)@([1-9][0-9]*)", str(task.get("request_ref", "")))
        if state in RESERVED and (not request or state != "blocked" and requests.get(request.group(1)) != int(request.group(2))):
            add(f"{task_id}: missing/stale USER or Jira request revision")
        if state in RESERVED:
            if not registry.get("setup_complete"):
                add(f"{task_id}: cannot issue work before setup_complete")
            if any(type(task.get(field)) is not int or task[field] < 1 for field in ("policy_revision", "charter_revision")):
                add(f"{task_id}: issued policy and charter revisions must be positive integers")
            if state != "blocked" and (task.get("policy_revision") != registry["policy_revision"] or task.get("charter_revision") != agents.get(assignee, {}).get("charter_revision")):
                add(f"{task_id}: stale policy or charter revision")
            if not is_sha(task.get("base_commit")):
                add(f"{task_id}: needs a full actual base_commit SHA")
            for field in ("branch", "worktree"):
                if not isinstance(task.get(field), str) or not task[field].strip() or "<" in task[field]:
                    add(f"{task_id}: missing prepared {field}")
            worktree = task.get("worktree")
            if isinstance(worktree, str) and not (PurePosixPath(worktree).is_absolute() or PureWindowsPath(worktree).is_absolute()):
                add(f"{task_id}: worktree must be an absolute path")
            if kind == "implementation" and not task["write_paths"]:
                add(f"{task_id}: implementation needs bounded write_paths")
            if not task["verification_profiles"]:
                add(f"{task_id}: needs relevant verification profiles")
            for key, values in ((assignee, live_agents), (task.get("branch"), branches), (worktree_key(task.get("worktree")), worktrees)):
                if key in values:
                    add(f"{task_id}: active assignee/branch/worktree already reserved by {values[key]}")
                values[key] = task_id
            if kind == "workspace":
                for output in outputs:
                    if isinstance(output, dict):
                        for key, values in ((output.get("branch"), branches), (worktree_key(output.get("worktree")), worktrees)):
                            if isinstance(key, str):
                                if key in values:
                                    add(f"{task_id}: workspace output already reserved by {values[key]}")
                                values[key] = task_id
            reservations.append((task_id, task))
        if kind not in {"workspace", "qa"} and state in {"review", "verified", "integrating", "done"} and not is_sha(task.get("candidate_commit")):
            add(f"{task_id}: submitted state needs immutable candidate_commit")
        if state == "done" and (not isinstance(task.get("completion_evidence"), str) or not task["completion_evidence"].strip()):
            add(f"{task_id}: done needs a Master completion_evidence reference")
        for key in task["contracts"]:
            if key not in contracts or (state in RESERVED - {"blocked"} and contracts[key].get("state") != "agreed"):
                add(f"{task_id}: missing or unagreed contract {key}")
        for key in task["verification_profiles"]:
            if key not in profiles:
                add(f"{task_id}: unregistered verification profile {key}")
        approval = task.get("governance_approval")
        scopes = effective_paths(task, registry)
        touches_governance = any(overlaps(s, p) for s in scopes for p in protected)
        touches_governance |= any(PurePosixPath(s.rstrip('/')).name in {"AGENTS.md", "AGENTS.override.md"} for s in scopes)
        if state in RESERVED and touches_governance and approval not in decisions:
            add(f"{task_id}: governance scope needs USER decision reference")
        promotion = task.get("promotion_authority")
        item = registry["work_items"].get(request.group(1), {}) if request else {}
        approved_plan = item.get("plan") or {}
        jira_promotion = item.get("completion_target") == "promoted" and approved_plan.get("promotion_authorized") is True and promotion == (approved_plan.get("approval") or {}).get("source_ref")
        if promotion and state in RESERVED - {"blocked"} and not (promotion in user_authorities or jira_promotion):
            add(f"{task_id}: promotion authority is missing in USER.md or the approved Jira plan")
        if promotion and not re.fullmatch(r"(?:DEC-[0-9]{4,}|RQ-[0-9]{4,}@[1-9][0-9]*|jira-comment:[0-9]+)", str(promotion)):
            add(f"{task_id}: promotion authority needs a retained USER/Jira source reference")
        if state == "done" and goal == "promoted":
            if not promotion or not is_sha(task.get("promoted_commit")):
                add(f"{task_id}: promoted completion needs authority and actual promoted_commit")
            if kind == "integration" and task.get("promoted_commit") != task.get("candidate_commit"):
                add(f"{task_id}: completed integration needs exact promoted_commit")
        dependencies = []
        for dependency in task["depends_on"]:
            if not isinstance(dependency, dict) or dependency.get("required_state") not in {"verified", "done"}:
                add(f"{task_id}: invalid dependency")
                continue
            dep_id = dependency.get("task_id")
            dependencies.append(dep_id)
            other = tasks.get(dep_id)
            if not other:
                add(f"{task_id}: missing dependency {dep_id}")
            elif state in RESERVED - {"blocked"}:
                acceptable = {"done"} if dependency["required_state"] == "done" else {"verified", "integrating", "done"}
                if other.get("state") not in acceptable:
                    add(f"{task_id}: dependency {dep_id} has not reached {dependency['required_state']}")
        graph[task_id] = dependencies
    for index, (left_id, left) in enumerate(reservations):
        for right_id, right in reservations[index + 1:]:
            if any(overlaps(a, b) for a in effective_paths(left, registry) for b in effective_paths(right, registry)) and not source_handoff(left_id, left, right_id, right):
                add(f"reservation overlap: {left_id} and {right_id}")
    visiting, visited = set(), set()

    def visit(node):
        if node in visiting:
            add(f"dependency cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    errors.extend(workflow.checks(root, registry, user_authorities))
    return sorted(set(errors))


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if check and result.returncode:
        raise ValueError(f"Git inspection failed: {' '.join(args)}\n{result.stderr.decode(errors='replace').strip()}")
    return result


def audit(root, registry, task_id, agent_id, code_root, head="HEAD", working=False):
    errors = checks(root, registry, ready=True)
    task = registry["tasks"].get(task_id)
    if not task or task.get("assignee") != agent_id:
        return errors + ["audit task must exist and belong to the evaluated agent"], []
    if errors:
        return errors, []
    if task.get("state") in {"draft", "cancelled"}:
        return ["cannot audit an unissued/cancelled task as authorized work"], []
    repo = Path(code_root).resolve()
    actual = Path(git(repo, "rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()
    if repo != actual:
        return ["code-root must be the exact Git worktree root"], []
    base = task["base_commit"]
    head_sha = git(repo, "rev-parse", "--verify", f"{head}^{{commit}}").stdout.decode().strip()
    git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    if git(repo, "merge-base", "--is-ancestor", base, head_sha, check=False).returncode:
        errors.append("assigned base_commit is not an ancestor of inspected candidate")
    paths = set(filter(None, git(repo, "diff", "--no-renames", "--name-only", "-z", base, head_sha, "--").stdout.decode(errors="surrogateescape").split("\0")))
    if working:
        current = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
        if head_sha != current:
            errors.append("working-tree inspection requires current HEAD")
        if repo != Path(task["worktree"]).resolve():
            errors.append("working-tree root does not match assigned worktree")
        branch = git(repo, "branch", "--show-current").stdout.decode().strip()
        if branch != task["branch"]:
            errors.append("working-tree branch does not match assignment")
        for args in (("diff", "--no-renames", "--name-only", "-z", "HEAD", "--"), ("ls-files", "--others", "--exclude-standard", "-z")):
            paths.update(filter(None, git(repo, *args).stdout.decode(errors="surrogateescape").split("\0")))
    scopes = effective_paths(task, registry)
    for path in sorted(paths):
        if not any(covers(scope, path) for scope in scopes):
            errors.append(f"out-of-scope changed path: {path}")
        if PurePosixPath(path).name in {"AGENTS.md", "AGENTS.override.md"} and not task.get("governance_approval"):
            errors.append(f"instruction change needs USER governance approval: {path}")
    if task.get("kind") == "integration":
        for source in task["merge_sources"]:
            sha = source["commit"]
            git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}")
            if git(repo, "merge-base", "--is-ancestor", sha, head_sha, check=False).returncode:
                errors.append(f"integration candidate does not preserve named source commit: {source['task_id']}")
    for dependency in task["depends_on"]:
        dep = registry["tasks"][dependency["task_id"]]
        sha = dep.get("candidate_commit")
        if is_sha(sha) and git(repo, "merge-base", "--is-ancestor", sha, base, check=False).returncode and task.get("kind") != "integration":
            errors.append(f"assigned base lacks exact code dependency: {dependency['task_id']}")
    if task.get("kind") == "qa" and task.get("qa_subject", {}).get("kind") == "candidate":
        if head_sha != task["qa_subject"].get("candidate_commit") or base != head_sha:
            errors.append("QA inspection must use the exact assigned candidate and base SHA")
    return sorted(set(errors)), sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "show", "audit"))
    parser.add_argument("--control-root", required=True)
    parser.add_argument("--ready", action="store_true", help="require completed bootstrap")
    parser.add_argument("--agent", help="agent whose assignment/diff is evaluated, not the caller")
    parser.add_argument("--task")
    parser.add_argument("--code-root")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--working-tree", action="store_true", help="include tracked dirty and untracked nonignored paths")
    args = parser.parse_args()
    root = Path(args.control_root).resolve()
    try:
        registry = json.loads((root / "REGISTRY.json").read_text(encoding="utf-8"))
        if not isinstance(registry, dict):
            raise ValueError("registry must be an object")
        if args.action == "show":
            if not args.agent and not args.task:
                raise ValueError("show requires --agent or --task")
            selected = registry.get("tasks", {})
            if args.task:
                if args.task not in selected:
                    raise ValueError("task not found; do not infer an assignment")
                selected = {args.task: selected[args.task]}
            if args.agent:
                if args.agent not in registry.get("agents", {}):
                    raise ValueError("agent not registered")
                selected = {k: v for k, v in selected.items() if v.get("assignee") == args.agent}
                if args.task and not selected:
                    raise ValueError("selected task belongs to another agent")
            source_keys = {str(task.get("request_ref", "")).split("@")[0] for task in selected.values()}
            result = {"registry_revision": registry.get("revision"), "policy_revision": registry.get("policy_revision"), "agent": registry.get("agents", {}).get(args.agent), "tasks": selected,
                      "work_items": {key: item for key, item in registry.get("work_items", {}).items() if key in source_keys}}
            print(json.dumps(result, indent=2))
            return 0
        if args.action == "check":
            errors = checks(root, registry, args.ready)
            result = {"ok": not errors, "setup_complete": registry.get("setup_complete"), "errors": errors}
        else:
            if not all((args.task, args.agent, args.code_root)):
                raise ValueError("audit requires --task, --agent, and --code-root")
            errors, paths = audit(root, registry, args.task, args.agent, args.code_root, args.head, args.working_tree)
            result = {"ok": not errors, "evaluated_agent": args.agent, "task": args.task, "changed_paths": paths, "errors": errors}
        print(json.dumps(result, indent=2))
        return 0 if not errors else 1
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps({"ok": False, "errors": [f"Inspection failed; re-read live records: {error}"]}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
