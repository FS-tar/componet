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
