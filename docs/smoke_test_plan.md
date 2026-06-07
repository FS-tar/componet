# Smoke Test Plan

Date: 2026-06-07
Worktree: `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\smoke-test`
Branch: `exp/smoke-test`

## Current Status

The first official-code smoke test is blocked by the lack of a usable Python command in the current shell.

Confirmed working:

- The current branch is `exp/smoke-test`.
- The current directory is the requested `smoke-test` worktree.
- `nvidia-smi` can see the NVIDIA GeForce RTX 3050 Laptop GPU with 4 GB VRAM.
- Driver version is `531.88`; driver-reported CUDA version is `12.1`.
- The operating system reports `Microsoft Windows NT 10.0.26200.0`.

Confirmed failing:

- `python scripts/check_env.py` fails before the script can start because `python` is not found.
- `python experiments/atari/run_ppo.py cnn-simple --help` fails for the same reason.
- `py --version` reports `No installed Python found!`.
- `pip`, `python -m pip`, and `conda` are unavailable.
- `where.exe python` finds no Python executable.
- `where.exe py` finds only `C:\Windows\py.exe`.

## First Smoke Test Choice

Prioritize Atari before Meta-World.

Reasons:

- `docs/environment_setup.md` and `docs/reproduction_plan_code.md` both recommend Atari as the first target.
- Atari has a smaller and less native-rendering-heavy dependency stack than Meta-World.
- Meta-World adds MuJoCo, OpenGL/GLFW, a GitHub-installed `metaworld` package, and CUDA wheel constraints that are higher-risk on native Windows.
- The Atari baseline can start with `cnn-simple`, which does not need previous CompoNet units or saved historical models.

Best first entrypoint:

```powershell
python experiments/atari/run_ppo.py cnn-simple --help
```

Do not run full training yet.

## Minimal Setup Command

Install or expose Python 3.10 first. After `python` is available, install only the Atari dependency set:

```powershell
python -m pip install --upgrade pip
python -m pip install -r experiments/atari/requirements.txt
```

If Atari ROM setup is missing after dependency installation, run:

```powershell
AutoROM --accept-license
```

Do not install Meta-World dependencies for the first smoke test.

## Next Validation Commands

After Python and Atari dependencies are available, rerun:

```powershell
python scripts/check_env.py
python experiments/atari/run_ppo.py cnn-simple --help
```

Expected success criteria:

- `scripts/check_env.py` prints Python, pip, operating system, `nvidia-smi`, and PyTorch status.
- `run_ppo.py cnn-simple --help` reaches tyro CLI output instead of failing at interpreter or import time.

## Smoke Test Gate

Only after the help command succeeds, design a tiny Atari PPO smoke run with:

- `cnn-simple`
- a single Atari mode
- very low `--total-timesteps`
- low `--num-envs`
- low `--num-steps`
- no `--track`
- no `--capture-video`
- no `--save-dir` unless a later evaluation smoke test requires a temporary model

The first run must stay under 5 minutes and must not generate large checkpoints, videos, datasets, or logs.

Suggested commit message:

```text
docs: record first smoke test environment check
```
