# Experiment Log

## 2026-06-06 Environment Check

Goal: inspect the current environment and design an installation plan without installing dependencies, running training, switching branches, or changing algorithm code.

### Repository Safety Checks

Command:

```powershell
git branch --show-current
```

Result:

```text
chore/env-check
```

Command:

```powershell
git status
```

Result:

```text
On branch chore/env-check
Your branch is up to date with 'origin/chore/env-check'.

nothing to commit, working tree clean
```

Command:

```powershell
pwd
```

Result:

```text
D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\env-check
```

### Files Read

- `AGENTS.md`
- `README.md`
- `experiments/atari/requirements.txt`
- `experiments/meta-world/requirements.txt`
- `.gitignore`
- `experiments/atari/run_ppo.py`
- `experiments/meta-world/run_sac.py`

### Environment Commands

Command:

```powershell
python --version
```

Result:

```text
Failed: python command not found in the current shell.
```

Command:

```powershell
python -m pip --version
```

Result:

```text
Failed: python command not found in the current shell.
```

Command:

```powershell
py --version
```

Result:

```text
Failed: C:\Windows\py.exe exists, but reports no installed Python.
```

Command:

```powershell
where.exe python
```

Result:

```text
Failed: no python executable found.
```

Command:

```powershell
where.exe py
```

Result:

```text
C:\Windows\py.exe
```

Command:

```powershell
conda --version
```

Result:

```text
Failed: conda command not found in the current shell.
```

Command:

```powershell
nvidia-smi
```

Result:

```text
NVIDIA-SMI 531.88
Driver Version: 531.88
CUDA Version: 12.1
GPU 0: NVIDIA GeForce RTX 3050 Laptop GPU
Memory: 4096 MiB total, 113 MiB used during check
GPU utilization: 0%
```

Command:

```powershell
[System.Environment]::OSVersion.VersionString
```

Result:

```text
Microsoft Windows NT 10.0.26200.0
```

Command:

```powershell
$PSVersionTable
```

Result:

```text
PowerShell 5.1.26100.8457
```

Command:

```powershell
Get-ComputerInfo -Property OsName,OsVersion,OsArchitecture
```

Result:

```text
Command completed, but the selected fields were blank in this shell.
```

Command:

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture
```

Result:

```text
Failed: permission denied by the current environment.
```

### Script Check

Command:

```powershell
python scripts/check_env.py
```

Result:

```text
Failed: python command not found in the current shell. The script could not start.
```

### Preliminary Conclusion

The machine has an NVIDIA GPU and driver-level CUDA visibility, but the project cannot proceed to dependency installation or smoke tests until Python is installed or exposed in PATH. PyTorch status cannot be checked through Python yet because Python itself is unavailable.

Atari should be the first smoke-test target after environment setup. Meta-World should wait until the Python and Atari path is validated.

### Diff Check

Command:

```powershell
git diff --stat
```

Result:

```text
.gitignore | 8 ++++++++
1 file changed, 8 insertions(+)
```

Note: `git diff --stat` only reports tracked-file changes, so the newly created untracked files are visible through `git status --short --untracked-files=all` instead.

## 2026-06-07 Smoke Test Preparation

Goal: prepare the first official-code smoke test without switching branches, running full training, installing dependencies, or generating large result files.

### Repository Safety Checks

Command:

```powershell
git branch --show-current
```

Result:

```text
exp/smoke-test
```

Command:

```powershell
git status --short --branch
```

Result:

```text
## exp/smoke-test...origin/exp/smoke-test
```

Command:

```powershell
Get-Location
```

Result:

```text
D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\smoke-test
```

### Files Read

- `AGENTS.md`
- `README.md`
- `docs/environment_setup.md`
- `docs/experiment_log.md`
- `docs/reproduction_plan_code.md`
- `docs/codebase_map.md`
- `experiments/atari/requirements.txt`
- `experiments/meta-world/requirements.txt`
- `scripts/check_env.py`
- `experiments/atari/run_ppo.py`
- `experiments/meta-world/run_sac.py`

### Environment Commands

Command:

```powershell
python scripts/check_env.py
```

Result:

```text
Failed: python command not found in the current shell. The script could not start.
PowerShell reported: python is not recognized as a cmdlet, function, script file, or runnable program.
```

Command:

```powershell
py --version
```

Result:

```text
No installed Python found!
```

Command:

```powershell
where.exe python
```

Result:

```text
INFO: Could not find files for the given pattern(s).
```

Command:

```powershell
where.exe py
```

Result:

```text
C:\Windows\py.exe
```

Command:

```powershell
conda --version
```

Result:

```text
Failed: conda command not found in the current shell.
```

Command:

```powershell
pip --version
```

Result:

```text
Failed: pip command not found in the current shell.
```

Command:

```powershell
python -m pip --version
```

Result:

```text
Failed: python command not found in the current shell.
```

Command:

```powershell
nvidia-smi
```

Result:

```text
NVIDIA-SMI 531.88
Driver Version: 531.88
CUDA Version: 12.1
GPU 0: NVIDIA GeForce RTX 3050 Laptop GPU
Memory: 4096 MiB total, 8 MiB used during check
GPU utilization: 0%
```

Command:

```powershell
[System.Environment]::OSVersion.VersionString
```

Result:

```text
Microsoft Windows NT 10.0.26200.0
```

### Entrypoint Help Check

Command:

```powershell
python experiments/atari/run_ppo.py cnn-simple --help
```

Result:

```text
Failed: python command not found in the current shell. The script could not start, so no Python package imports or CLI parsing were reached.
PowerShell reported: python is not recognized as a cmdlet, function, script file, or runnable program.
```

### Dependency Assessment

The first missing dependency is Python itself. Because no usable Python executable is available, PyTorch, pip, Gymnasium, ALE, tyro, and other Python packages cannot be checked yet.

Atari should be the first smoke-test target after Python is available. The relevant dependency file is `experiments/atari/requirements.txt`, with the main required packages including:

- `torch==2.1.0`
- `torchvision`
- `gym==0.23.1`
- `gymnasium[atari]==0.28.1`
- `ale-py==0.8.1`
- `autorom[accept-rom-license]==0.4.2`
- `autorom-accept-rom-license==0.6.1`
- `stable-baselines3==2.0.0`
- `tyro==0.5.10`
- `tensorboard==2.11.2`
- `opencv-python==4.7.0.72`

Meta-World should wait because its requirements include MuJoCo, OpenGL/GLFW, GitHub-installed `metaworld`, and Linux-style CUDA wheel packages that are higher-risk on native Windows.

### Smoke Test Decision

Preferred first smoke-test entrypoint:

```powershell
python experiments/atari/run_ppo.py cnn-simple --help
```

Reason: `experiments/atari/run_ppo.py` is the official single-run PPO entrypoint, and `cnn-simple` avoids CompoNet previous-unit requirements for the first baseline check.

No training was run in this step.

### Next Minimal Operation

Install or expose Python 3.10 first, then install only the Atari dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r experiments/atari/requirements.txt
```

If Atari ROM setup is still missing after dependency installation:

```powershell
AutoROM --accept-license
```

Then rerun:

```powershell
python scripts/check_env.py
python experiments/atari/run_ppo.py cnn-simple --help
```

Only after `--help` succeeds should a tiny `cnn-simple` Atari smoke test be designed. Do not run any full training or any run expected to exceed 5 minutes.

### Suggested Commit Message

```text
docs: record first smoke test environment check
```

## 2026-06-07 Atari Help Smoke-Test Step

Goal: start the first smoke-test step by checking the official Atari training entrypoint help output only. No dependency installation, formal training, branch switching, or large output generation was performed.

### Repository Safety Checks

Command:

```powershell
git branch --show-current
```

Result:

```text
exp/smoke-test
```

Command:

```powershell
git status
```

Result:

```text
On branch exp/smoke-test
Your branch is up to date with 'origin/exp/smoke-test'.

nothing to commit, working tree clean
```

Command:

```powershell
Get-Location
```

Result:

```text
D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\smoke-test
```

### Environment Checks

Command:

```powershell
python --version
```

Result:

```text
Failed: python command not found in the current shell.
PowerShell reported: python is not recognized as a cmdlet, function, script file, or runnable program.
```

Command:

```powershell
pip --version
```

Result:

```text
Failed: pip command not found in the current shell.
PowerShell reported: pip is not recognized as a cmdlet, function, script file, or runnable program.
```

Command:

```powershell
python scripts/check_env.py
```

Result:

```text
Failed: python command not found in the current shell. The environment check script could not start.
```

### Files Read

- `docs/smoke_test_plan.md`
- `docs/environment_setup.md`
- `docs/reproduction_plan_code.md`
- `docs/codebase_map.md`
- `README.md`
- `experiments/atari/requirements.txt`

### Atari Entrypoint

The first Atari training entrypoint is:

```text
experiments/atari/run_ppo.py
```

This is the official single-run PPO entrypoint described by `README.md`, `docs/codebase_map.md`, and `docs/smoke_test_plan.md`. The first model choice remains `cnn-simple` because it does not require previous CompoNet units or saved historical models.

### Help Command

Command:

```powershell
python experiments/atari/run_ppo.py cnn-simple --help
```

Result:

```text
Failed before Python started the script.
PowerShell reported: python is not recognized as a cmdlet, function, script file, or runnable program.
```

The `--help` check did not reach the Python interpreter, package imports, or tyro CLI parsing. Therefore the current blocker is Python itself, not yet `torch`, `tyro`, `gymnasium`, `ale-py`, or another Atari package.

### Minimum Install Command

First install or expose Python 3.10 in PATH. Then install only the Atari dependency set:

```powershell
python -m pip install --upgrade pip
python -m pip install -r experiments/atari/requirements.txt
```

If Atari ROM setup later fails after dependencies are installed:

```powershell
AutoROM --accept-license
```

### Next Step

After Python and Atari requirements are available, rerun:

```powershell
python scripts/check_env.py
python experiments/atari/run_ppo.py cnn-simple --help
```

Do not run training until the help command succeeds.

### Suggested Commit Message

```text
docs: record atari help smoke test blocker
```
