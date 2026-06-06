"""Print basic environment information for CompoNet reproduction checks."""

from __future__ import annotations

import importlib.util
import os
import platform
import subprocess
import sys


def print_section(title: str) -> None:
    print()
    print(f"== {title} ==")


def run_command(args: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        return 127, "command not found"
    except subprocess.TimeoutExpired:
        return 124, "command timed out"

    output = (completed.stdout or "").strip()
    error = (completed.stderr or "").strip()
    combined = output if output else error
    return completed.returncode, combined


def print_python_info() -> None:
    print_section("Python")
    print(f"executable: {sys.executable}")
    print(f"version: {sys.version.replace(os.linesep, ' ')}")


def print_pip_info() -> None:
    print_section("pip")
    code, output = run_command([sys.executable, "-m", "pip", "--version"])
    print(f"available: {code == 0}")
    print(f"result: {output}")


def print_os_info() -> None:
    print_section("Operating system")
    print(f"platform: {platform.platform()}")
    print(f"system: {platform.system()}")
    print(f"release: {platform.release()}")
    print(f"version: {platform.version()}")
    print(f"machine: {platform.machine()}")


def print_nvidia_smi_info() -> None:
    print_section("nvidia-smi")
    code, output = run_command(["nvidia-smi"])
    print(f"available: {code == 0}")
    print(output)


def print_torch_info() -> None:
    print_section("PyTorch")
    torch_spec = importlib.util.find_spec("torch")
    print(f"installed: {torch_spec is not None}")
    if torch_spec is None:
        return

    import torch

    print(f"version: {torch.__version__}")
    print(f"cuda build: {torch.version.cuda}")
    cuda_available = torch.cuda.is_available()
    print(f"torch cuda available: {cuda_available}")
    print(f"cuda device count: {torch.cuda.device_count()}")
    if cuda_available:
        for index in range(torch.cuda.device_count()):
            print(f"cuda device {index}: {torch.cuda.get_device_name(index)}")


def main() -> None:
    print_python_info()
    print_pip_info()
    print_os_info()
    print_nvidia_smi_info()
    print_torch_info()


if __name__ == "__main__":
    main()
