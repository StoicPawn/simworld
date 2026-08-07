# SimWorld agentic operations

This document explains how SimWorld is developed and run remotely from phone or PC through GitHub Actions.

## Two independent remote controls

### 1. SimWorld Development Agent

Use `.github/workflows/agent-dev.yml` when you want Codex to **change the repository**.

From GitHub Actions choose **SimWorld Development Agent**, enter a bounded task, choose `auto`, `local`, or `cloud`, and start the run.

The workflow:

1. resolves the requested base ref;
2. in `auto` mode checks for an online, idle self-hosted runner with label `agent-pc`;
3. uses the PC when available, otherwise GitHub cloud;
4. runs Codex through `scripts/agent_loop.py` with a finite iteration budget;
5. validates after every successful Codex iteration;
6. creates and pushes an isolated `agent/*` branch only after validation passes;
7. opens a **draft PR**;
8. never merges automatically.

The agent is required to read `AGENTS.md`, `docs/PROJECT_MATRIX.md`, `.agent/project_state.md` and `.agent/roadmap.yaml` before changing code.

### 2. Run SimWorld

Use `.github/workflows/simulate.yml` when you want to **execute the simulator without changing code**.

Inputs currently include world config, seed, horizon and execution environment. The Phase-0 runner produces a downloadable GitHub Actions artifact containing:

- `metadata.json`;
- `events.jsonl`;
- `world_final.json`;
- `summary.md`.

The current `configs/worlds/kernel_smoke.json` intentionally demonstrates two distant events at the same simulated time, one isolated causal continuation, and a later event where previously separate histories converge.

As SimWorld grows, this workflow remains the stable remote entry point while the simulation config/schema becomes richer.

## Execution capabilities

The router treats `agent-pc` and GitHub cloud as different capability classes rather than pretending they are identical.

GitHub cloud is expected to provide:

- Python;
- ephemeral build/test environment;
- Codex through `OPENAI_API_KEY` for development-agent fallback;
- short/medium simulations.

The PC runner may later additionally provide:

- local Llama or other local models;
- GPU;
- larger RAM;
- Docker caches;
- long simulations;
- local datasets that are deliberately not stored in Git.

Future routing should evolve from the current `agent-pc online + idle` check into explicit capability matching.

## One-time PC setup

The repository cannot register your physical PC by itself. On the PC:

1. Open repository **Settings → Actions → Runners → New self-hosted runner**.
2. Select the correct OS/architecture.
3. Run the commands GitHub shows at that moment; the registration token is temporary.
4. Add the custom label `agent-pc`.
5. Confirm GitHub shows the runner as **Online / Idle**.
6. Install Python 3.11+ and Git.
7. Install Codex CLI and verify `codex --version`.
8. Authenticate Codex for the account under which the runner service executes, or provide an API-key based setup appropriate to that runner.
9. Optionally install the GitHub runner as a service so it becomes available after reboot.

Do not place registration tokens, API keys or Codex credentials in the repository.

## Cloud fallback credential

For the GitHub-hosted development-agent fallback, create the repository Actions secret:

`OPENAI_API_KEY`

Path: **Settings → Secrets and variables → Actions → New repository secret**.

The cloud workflow fails explicitly if this secret is absent. Simulation-only runs do not currently require the secret.

## Launching from a phone

From the GitHub app or mobile browser:

1. open `StoicPawn/simworld`;
2. open **Actions**;
3. select **SimWorld Development Agent** to request code changes, or **Run SimWorld** to run a world;
4. press **Run workflow**;
5. enter the task/configuration;
6. use `auto` unless you explicitly want to force PC or cloud;
7. inspect logs and, for development tasks, review the resulting draft PR before merge.

## Current limitation while PRs are stacked

Until the kernel PR and automation PR are merged into `main`, launch these workflows from the branch that contains them. After merge, normal use should launch from `main` and leave `base_ref` blank.

## Guardrails

Initial defaults intentionally prioritize auditability over autonomy:

- 3–10 Codex iterations, default 6;
- per-job timeout;
- stop after repeated equivalent failures;
- no direct push to `main`;
- no automatic merge;
- no production access;
- no secret mutation;
- validation before commit/push;
- draft PR as the final development output.

## Planned evolution

The same infrastructure is intended to support three eventual commands:

- **BUILD** — implement a bounded SimWorld capability and return a PR;
- **RUN** — execute one or many forward simulations and return artifacts/statistics;
- **INFER** — later run counterfactual/abductive inference over observations and return probability distributions over latent explanations.

The third command belongs to the long-term inverse-inference/geopolitical phase and must not be implemented prematurely.
