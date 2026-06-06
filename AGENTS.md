# AGENTS.md

## Project Goal

This repository is my reproduction and study project for the paper:

Self-Composing Policies for Scalable Continual Reinforcement Learning

The official method is CompoNet. My goals are:

1. Understand the paper deeply.
2. Understand the official codebase.
3. Reproduce at least one small official experiment or smoke test.
4. Document all commands, errors, fixes, and results.
5. Prepare clear explanations for academic discussion with my advisor.

## Working Rules for Codex

1. Do not make large unrelated changes.
2. Do not rewrite the whole repository.
3. Before modifying code, explain the intended change.
4. Prefer small, reviewable commits.
5. If an experiment is expensive, first create or run a smoke test.
6. Do not commit large generated files, checkpoints, datasets, logs, or videos.
7. Put study notes under `docs/`.
8. Put experiment logs under `docs/experiment_log.md`.
9. Put reproduction notes under `docs/reproduction_plan.md`.
10. Put paper explanations under `docs/paper_summary.md`.
11. Put codebase explanations under `docs/codebase_map.md`.
12. Put questions for advisor under `docs/advisor_questions.md`.
13. Do not delete official code unless explicitly asked.
14. If a command fails, analyze the error first. Fix only the most likely cause, then rerun.

## Current Priority

The first priority is understanding and running the official implementation, not creating a new implementation from scratch.

## Important Files

- `paper/self_composing_policies.pdf`: paper PDF.
- `README.md`: official repository README.
- `componet/`: implementation of the CompoNet architecture.
- `experiments/atari/`: Atari experiments.
- `experiments/meta-world/`: Meta-World experiments.
- `utils/`: shared utilities.

## Documentation Requirements

Codex should create or update:

- `docs/paper_summary.md`
- `docs/reproduction_plan.md`
- `docs/codebase_map.md`
- `docs/experiment_log.md`
- `docs/open_questions.md`
- `docs/advisor_explanation.md`

## Experiment Rules

Before running a full experiment:

1. Inspect the script and CLI options.
2. Run the script with `--help`.
3. Identify the shortest possible smoke test.
4. Run the smoke test first.
5. Record command, environment, output, error, and result.

## Git Rules

After each meaningful step, suggest a commit message.

Preferred commit types:

- `docs:` for notes and documentation
- `chore:` for environment setup
- `test:` for smoke tests
- `fix:` for bug fixes
- `exp:` for experiment runs