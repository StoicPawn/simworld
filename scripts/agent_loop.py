"""Bounded autonomous development loop for SimWorld.

The loop deliberately keeps orchestration deterministic: Codex proposes/implements changes,
while Git, validation, iteration limits and publication remain controlled by this script/workflow.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".agent" / "runs"


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable {name} is empty")
    return value


def run(
    command: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        timeout=timeout,
    )


def slugify(value: str, *, limit: int = 42) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return (value[:limit].rstrip("-") or "task")


def set_github_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def validate(log_path: Path) -> tuple[bool, str]:
    completed = run(
        [sys.executable, "scripts/validate.py"],
        check=False,
        capture=True,
        timeout=900,
    )
    output = completed.stdout or ""
    log_path.write_text(output, encoding="utf-8")
    print(output, end="")
    return completed.returncode == 0, output[-12_000:]


def codex_iteration(prompt: str, log_path: Path) -> tuple[bool, str]:
    executable = os.environ.get("CODEX_EXECUTABLE", "codex")
    model = os.environ.get("CODEX_MODEL", "").strip()
    timeout_seconds = int(os.environ.get("CODEX_ITERATION_TIMEOUT_SECONDS", "1200"))

    command = [
        executable,
        "--ask-for-approval",
        "never",
        "exec",
        "--sandbox",
        "workspace-write",
        "--ephemeral",
        "--json",
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)

    try:
        completed = run(command, check=False, capture=True, timeout=timeout_seconds)
        output = completed.stdout or ""
        log_path.write_text(output, encoding="utf-8")
        print(output, end="")
        return completed.returncode == 0, output[-16_000:]
    except subprocess.TimeoutExpired as exc:
        output = f"Codex iteration timed out after {timeout_seconds}s\n{exc}"
        log_path.write_text(output, encoding="utf-8")
        print(output)
        return False, output


def changed_files() -> str:
    result = run(["git", "status", "--short"], capture=True)
    return (result.stdout or "").strip()


def main() -> int:
    task = env_required("AGENT_TASK")
    requested = int(os.environ.get("MAX_ITERATIONS", "6"))
    max_iterations = max(1, min(requested, 10))
    run_id = os.environ.get("RUN_ID") or datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    branch = f"agent/{slugify(run_id, limit=28)}-{slugify(task)}"

    RUNS.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS / slugify(run_id, limit=60)
    run_dir.mkdir(parents=True, exist_ok=True)

    # The workflow checks out the requested base ref. The loop creates an isolated branch from it.
    run(["git", "checkout", "-b", branch])
    run(["git", "config", "user.name", "simworld-agent"])
    run(["git", "config", "user.email", "simworld-agent@users.noreply.github.com"])

    previous_failure = ""
    repeated_failures = 0

    for iteration in range(1, max_iterations + 1):
        prompt = f"""
You are implementing one bounded task in the SimWorld repository.

TASK:
{task}

MANDATORY CONTEXT:
- Read AGENTS.md first.
- Read docs/PROJECT_MATRIX.md.
- Read .agent/project_state.md and .agent/roadmap.yaml.
- Respect the current project phase and architectural invariants.
- Do not commit, push, merge, modify secrets, or change repository permissions.
- Do not weaken tests merely to make them pass.
- Keep the change tightly scoped to the task.

VALIDATION FEEDBACK FROM THE PREVIOUS ITERATION:
{previous_failure or 'None; this is the first iteration.'}

Implement the task in the working tree. Inspect existing code before editing. Finish after making the
best coherent change you can in this iteration; the outer controller will run validation.
""".strip()

        ok, agent_tail = codex_iteration(prompt, run_dir / f"codex-{iteration}.log")
        if not ok:
            failure = f"Codex exited unsuccessfully. Tail:\n{agent_tail}"
        else:
            valid, validation_tail = validate(run_dir / f"validation-{iteration}.log")
            if valid:
                status = changed_files()
                if not status:
                    print("Validation passed but Codex produced no repository changes.")
                    return 2
                print("Changes selected for commit:\n" + status)
                run(["git", "add", "-A"])
                run(["git", "diff", "--cached", "--check"])
                run(["git", "commit", "-m", f"Agent: {task[:72]}"])
                run(["git", "push", "-u", "origin", branch])
                set_github_output("branch", branch)
                print(f"AGENT_BRANCH={branch}")
                return 0
            failure = f"Repository validation failed. Tail:\n{validation_tail}"

        fingerprint = failure[-4000:]
        if fingerprint == previous_failure[-4000:]:
            repeated_failures += 1
        else:
            repeated_failures = 1
        previous_failure = failure

        if repeated_failures >= 3:
            print("Stopping after three equivalent consecutive failures.")
            return 3
        time.sleep(1)

    print(f"Stopping after maximum iteration budget ({max_iterations}).")
    print("Current changes:\n" + (changed_files() or "<none>"))
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
