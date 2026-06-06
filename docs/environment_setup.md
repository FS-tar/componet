# Environment Setup

Date: 2026-06-06
Worktree: `D:\fishstar\software\PyCharm 2024.3.5\projects\componet\componet-worktrees\env-check`
Branch: `chore/env-check`

## Current Status

This machine is not ready for official smoke tests yet because no usable Python command is available in the current shell:

- `python` is not found.
- `py` exists at `C:\Windows\py.exe`, but reports no installed Python.
- `conda` is not found.

GPU hardware is visible through `nvidia-smi`:

- GPU: NVIDIA GeForce RTX 3050 Laptop GPU, 4 GB VRAM
- Driver: 531.88
- CUDA reported by driver: 12.1

The next setup step should be creating an isolated Python environment before installing either experiment dependency set.

## Atari Experiments

Requirements file: `experiments/atari/requirements.txt`

Main dependency groups:

- Deep learning: `torch==2.1.0`, `torchvision`
- Atari environments: `gym==0.23.1`, `gymnasium[atari]==0.28.1`, `ale-py==0.8.1`
- Atari ROM setup: `autorom[accept-rom-license]==0.4.2`, `autorom-accept-rom-license==0.6.1`
- RL utilities: `stable-baselines3==2.0.0`, `tyro==0.5.10`
- Logging and visualization: `tensorboard==2.11.2`
- Image processing: `opencv-python==4.7.0.72`

Expected installation difficulty: medium.

Atari is simpler than Meta-World, but still needs careful handling because ALE/ROM setup can fail if ROM installation or package versions are inconsistent. It should be feasible on Windows after Python is installed, although a Linux environment may be smoother for full reproducibility.

Expected runtime: high for paper-scale runs because defaults use `total_timesteps=1e6`, `num_envs=8`, and PPO training. A tiny smoke test should reduce timesteps and environment count.

GPU need: useful but not strictly required for a tiny `cnn-simple` smoke test. The detected RTX 3050 4 GB should be enough for small Atari smoke runs, but may be tight for larger models or long experiments.

Smoke-test suitability: best first target. Recommended first smoke test after Python and dependencies are ready:

```powershell
python experiments/atari/run_ppo.py cnn-simple --help
```

Then run a very small `cnn-simple` PPO command with low `--total-timesteps`, low `--num-envs`, no video capture, no W&B tracking, and no model save unless explicitly needed.

## Meta-World Experiments

Requirements file: `experiments/meta-world/requirements.txt`

Main dependency groups:

- Deep learning: `torch==2.1.2`
- CUDA wheel packages: `nvidia-cublas-cu12`, `nvidia-cuda-runtime-cu12`, `nvidia-cudnn-cu12`, and related CUDA 12 packages
- Continuous-control environments: `gymnasium==0.29.1`, `mujoco==2.3.7`
- Meta-World: `metaworld` installed from GitHub commit `c822f28f582ba1ad49eb5dcf61016566f28003ba`
- RL utilities: `stable-baselines3==2.2.1`, `tyro==0.6.3`
- Tracking and logging: `wandb==0.16.1`, `tensorboard==2.15.1`
- Scientific and plotting stack: `numpy`, `scipy`, `pandas`, `matplotlib`, `imageio`
- Rendering/native support: `glfw`, `PyOpenGL`

Expected installation difficulty: high.

Meta-World is likely harder on Windows because it depends on MuJoCo, OpenGL/GLFW rendering support, and a GitHub-installed Meta-World package. The dependency file also includes Linux-style CUDA 12 wheel packages such as `nvidia-*` and `triton`, which may not match a native Windows Python environment cleanly.

Expected runtime: high for paper-scale runs because defaults use `total_timesteps=1e6`, large replay buffers, and repeated evaluations. A smoke test should use tiny timestep counts and probably run without rendering.

GPU need: useful for SAC training, but a minimal CPU smoke test may be possible after installation. The detected RTX 3050 4 GB is enough for basic checks but may be limited for long experiments.

Smoke-test suitability: second priority. It is valuable for reproducing the paper but should wait until Atari and core environment setup are working.

## Recommended Setup Order

1. Install or expose Python in PATH.
2. Create an isolated environment for this project.
3. Install only the Atari requirements first.
4. Run `python scripts/check_env.py`.
5. Run Atari script `--help`.
6. Design and run a minimal Atari smoke test.
7. Only after Atari works, evaluate whether to install Meta-World natively on Windows or use WSL/Linux.

Recommended Python target: a Python version compatible with PyTorch 2.1.x, such as Python 3.10.

## First Smoke-Test Choice

Prioritize Atari first.

Reasons:

- The Atari dependency stack is smaller and less native-rendering-heavy than Meta-World.
- The official Atari entrypoint has clear small-run controls such as `total_timesteps`, `num_envs`, and `num_steps`.
- Meta-World introduces MuJoCo, OpenGL/GLFW, GitHub installation, and likely Windows compatibility friction.
- A tiny Atari `cnn-simple` PPO run is the shortest path to validating official training code without changing algorithm code.
