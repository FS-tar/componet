# Smoke Test Plan

Date: 2026-06-07
Worktree: `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\smoke-test`
Branch: `exp/smoke-test`

## Current Status

The first official-code smoke test is ready for the shortest smoke-run design stage. The NumPy compatibility risk has been checked: the project `.venv` currently uses NumPy `1.26.4`, and the previous `_ARRAY_API not found` warning/error stream no longer appears in `scripts/check_env.py` or `run_ppo.py cnn-simple --help`.

Confirmed working:

- The current branch is `exp/smoke-test`.
- The current directory is the requested `smoke-test` worktree.
- `nvidia-smi` can see the NVIDIA GeForce RTX 3050 Laptop GPU with 4 GB VRAM.
- Driver version is `531.88`; driver-reported CUDA version is `12.1`.
- The operating system reports `Microsoft Windows NT 10.0.26200.0`.

Confirmed failing:

- `python --version` fails because `python` is not found.
- `pip --version` fails because `pip` is not found.
- `py -0p` reports `No installed Pythons found!`.
- `py -3.10 --version` reports `No installed Python found!`.
- `python scripts/check_env.py` fails before the script can start because `python` is not found.
- `python experiments/atari/run_ppo.py cnn-simple --help` fails for the same reason.
- `py --version` reports `No installed Python found!`.
- `pip`, `python -m pip`, and `conda` are unavailable.
- `where.exe python` finds no Python executable.
- `where.exe py` finds only `C:\Windows\py.exe`.
- Latest repository check was run from branch `exp/smoke-test` in `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\smoke-test`.
- `venv` does not exist in the worktree.
- `.venv` does not exist in the worktree.
- `.\venv\Scripts\python.exe` does not exist.
- `.\.venv\Scripts\python.exe` does not exist.
- `..\..\.venv\Scripts\python.exe` exists in the main project directory.
- `..\..\.venv\Scripts\python.exe --version` fails with `Unable to create process using '"C:\Users\86157\AppData\Local\Programs\Python\Python310\python.exe" --version'`.
- `..\..\.venv\Scripts\python.exe -m pip --version` fails with the same missing base interpreter path.
- Latest activated-environment check printed no `$env:VIRTUAL_ENV` value.
- `Get-Command python` failed in the latest command execution environment.
- `python --version` and `python -m pip --version` failed in the latest command execution environment.
- Absolute path invocation with `& "D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe" --version` fails with `Unable to create process using '"C:\Users\86157\AppData\Local\Programs\Python\Python310\python.exe" --version'`.
- Absolute path invocation with `& "D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe" -m pip --version` fails with the same missing base interpreter path.
- Manual PyCharm Terminal confirmation shows the project `.venv` is usable there.
- Manual `VIRTUAL_ENV` is `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv`.
- Manual Python version is `3.10.11`.
- Manual pip comes from the project `.venv`.
- Manual base executable check succeeded.
- Full Access allowed Codex to execute `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe`.
- Codex confirmed Python `3.10.11`.
- Codex confirmed pip `26.1.2` from the project `.venv`.
- `python -m pip install --upgrade pip` succeeded in the project `.venv`; pip was already satisfied.
- `python -m pip install -r experiments/atari/requirements.txt` succeeded; Atari packages were already satisfied.
- `scripts/check_env.py` succeeded with exit code 0.
- `experiments/atari/run_ppo.py cnn-simple --help` succeeded with exit code 0 and printed tyro CLI help.
- NumPy compatibility warnings/errors appeared during `check_env.py` and `--help`: NumPy 2.2.6 is incompatible with some modules compiled against NumPy 1.x, with `_ARRAY_API not found`.
- NumPy compatibility recheck confirmed NumPy `1.26.4` before and after `pip install "numpy<2"`.
- `pip install "numpy<2"` succeeded and reported the requirement was already satisfied.
- After the NumPy recheck, `scripts/check_env.py` succeeded with no `_ARRAY_API not found` warning/error.
- After the NumPy recheck, `run_ppo.py cnn-simple --help` succeeded with no `_ARRAY_API not found` warning/error.

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

Latest result: the help command was attempted and failed before Python started the script because `python` is not available in the shell. The missing dependency at this stage is Python itself, not yet `torch`, `tyro`, `gymnasium`, or `ale-py`.

Latest result: Full Access allowed Codex to use the project `.venv` directly. Atari requirements are installed in the project `.venv`; NumPy is `1.26.4`; `scripts/check_env.py` exits successfully; and `run_ppo.py cnn-simple --help` exits successfully while printing the expected tyro CLI options. The previous NumPy `_ARRAY_API not found` warning/error stream is gone.

Do not run full training yet.

## Minimal Setup Command

Candidate shortest smoke-run command to review next, but not execute yet:

```powershell
& "D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe" experiments/atari/run_ppo.py cnn-simple --total-timesteps 32 --num-envs 1 --num-steps 8 --num-minibatches 1 --update-epochs 1 --no-track --no-capture-video
```

If NumPy is fixed first, rerun validation before the true smoke command:

```powershell
& "D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe" scripts/check_env.py
& "D:\fishstar\software\PyCharm 2024.3.5\projects\componet\.venv\Scripts\python.exe" experiments/atari/run_ppo.py cnn-simple --help
```

If Atari ROM setup is missing after dependency installation, run:

```powershell
AutoROM --accept-license
```

Do not install Meta-World dependencies for the first smoke test.

## Next Validation Commands

After Atari dependencies and help output are confirmed manually, the next Codex step should be documentation and planning for a tiny smoke run, not training.

Do not run the Atari entrypoint without `--help` until the help command succeeds.

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
docs: record atari requirements and help check
```
