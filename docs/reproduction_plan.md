# CompoNet 复现规划

说明：当前本地仓库缺少 `paper/self_composing_policies.pdf`，复现规划基于官方 README、本地实验脚本和论文官方页面整理。所有实验命令执行前都应记录到 `docs/experiment_log.md`：命令、环境、输出、错误、修复和结果。本规划不要求提交 `agents/`、`runs/`、`videos/`、模型 checkpoint 或大型数据文件。

## Level 1: 跑通代码和环境检查

目标：确认仓库结构、Python 环境、依赖入口和 CLI 参数，不开始长训练。

操作步骤：

1. 确认当前目录是项目根目录。
2. 查看 Python、PyTorch、CUDA 是否可用。
3. 检查 Atari 和 Meta-World requirements 文件。
4. 在安装依赖前先运行 help，判断缺失依赖集中在哪些包。
5. 阅读 `run_experiments.py` 打印的官方批量命令，不直接跑长实验。

命令：

```powershell
python --version
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
Get-Content experiments\atari\requirements.txt
Get-Content experiments\meta-world\requirements.txt
cd experiments\atari
python run_ppo.py --help
cd ..\meta-world
python run_sac.py --help
python run_experiments.py --algorithm componet --seed 1 --start-mode 0 --no-run
```

验收标准：

- `run_ppo.py --help` 和 `run_sac.py --help` 至少能展示 CLI 参数，或清楚定位缺失依赖。
- 记录 Python、PyTorch、CUDA、Gymnasium、ALE、Meta-World 版本。
- 不启动默认 `1e6` timesteps 的训练。

可能风险：

- 当前环境可能没有安装 `tyro`、`gymnasium`、`stable-baselines3`、`ale-py`、`metaworld`。
- Windows 上 Atari ROM / ALE 安装可能需要额外步骤。
- Meta-World 依赖可能和 Python 版本、MuJoCo 版本冲突。

## Level 2: 跑通一个短 smoke test

目标：用极短步数验证训练脚本能创建环境、初始化模型、写 TensorBoard，并完成一次最小训练循环。

优先选择 Atari Freeway，因为单任务 smoke test 不需要加载前序模型。

Atari smoke test 命令：

```powershell
cd experiments\atari
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=0 --total-timesteps=1024 --num-envs=1 --num-steps=32 --num-minibatches=1 --cuda=False
```

Meta-World 备选 smoke test 命令：

```powershell
cd experiments\meta-world
python run_sac.py --model-type=simple --task-id=0 --total-timesteps=1000 --learning-starts=100 --random-actions-end=200 --cuda=False
```

验收标准：

- 能打印 run name、model type/device。
- 能初始化环境并进入训练循环。
- 能生成 `runs/` 下 TensorBoard 事件文件。
- 如果失败，`docs/experiment_log.md` 中必须记录完整错误和最可能原因，只修一个最可能原因后重试。

可能风险：

- `total_timesteps=1024` 对 PPO 只用于管线验证，不代表算法有效。
- Atari 环境可能因 ROM、环境 id、mode 支持失败。
- Meta-World 可能因图形/MuJoCo 后端、依赖版本失败。

## Level 3: 跑通一个小规模正式实验

目标：在很小任务序列上跑出 baseline 和 CompoNet 的最小对比链路，验证 `prev_units`、保存路径和模型加载逻辑。

推荐方案 A：Freeway 前两个 mode。

命令：

```powershell
cd experiments\atari
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=0 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents
python run_ppo.py --model-type=cnn-componet --env-id=ALE/Freeway-v5 --mode=1 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents --prev-units agents/ALE-Freeway-v5_0__cnn-simple__run_ppo__1 --componet-finetune-encoder
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=1 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents
```

推荐方案 B：Meta-World 前两个 task。

命令：

```powershell
cd experiments\meta-world
python run_sac.py --model-type=simple --task-id=0 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents
python run_sac.py --model-type=componet --task-id=1 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents --prev-units agents/task_0__simple__run_sac__1
python run_sac.py --model-type=simple --task-id=1 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents
```

验收标准：

- 第一任务模型能保存到 `agents/`。
- 第二任务 CompoNet 能通过 `--prev-units` 加载第一任务模型。
- baseline 与 CompoNet 都能完成小规模训练并写入 TensorBoard。
- `agents/` 和 `runs/` 不提交到 git。

可能风险：

- Atari run name 对 `mode` 和 `env_id` 很敏感，路径必须和脚本生成名称完全一致。
- 小规模训练可能没有明显性能提升，只验收链路，不验收论文指标。
- `--componet-finetune-encoder` 在官方 Atari 批量脚本中默认给 CompoNet 使用，但是否用于所有论文实验需继续核对。

## Level 4: 复现论文中的一个主要图或表的缩小版

目标：用官方压缩数据或 Level 3 的小规模结果，跑通结果处理和绘图流程。

操作步骤：

1. 解压 `experiments/atari/data.tar.xz` 或 `experiments/meta-world/data.tar.xz` 到对应实验目录下的 `data/`。
2. 优先使用官方数据运行 `process_results.py`，验证指标计算逻辑。
3. 如果使用小规模 runs，则只生成缩小版趋势图或表格，不声称复现论文数值。

Atari 命令：

```powershell
cd experiments\atari
python process_results.py --data-dir=data/envs/Freeway --eval-results=data/eval_results.csv
python process_results.py --data-dir=data/envs/SpaceInvaders --eval-results=data/eval_results.csv
```

Meta-World 命令：

```powershell
cd experiments\meta-world
python process_results.py --runs-dir=runs --save-csv=data/agg_results.csv --eval-csv=data/eval_results.csv
```

验收标准：

- 能生成或打印 Average Performance / Forward Transfer 相关汇总。
- 知道 `process_results.py` 需要哪些 TensorBoard scalar 或 CSV。
- 文档中明确区分“官方数据复现绘图流程”和“本地训练复现指标”。

可能风险：

- `data.tar.xz` 解压后路径结构必须和脚本默认参数一致。
- TensorBoard event scalar 名称缺失会导致处理脚本跳过 runs。
- 官方数据能复现图表流程，但不能证明本地训练完全复现。

## Level 5: 尝试完整复现

目标：接近论文设置，按默认 `1e6` timesteps/task、10 seeds、完整任务序列运行。

Atari SpaceInvaders 完整序列命令示例：

```powershell
cd experiments\atari
python run_experiments.py --algorithm from-scratch --env ALE/SpaceInvaders-v5 --start-mode 0 --first-mode 0 --last-mode 9 --seed 1
python run_experiments.py --algorithm componet --env ALE/SpaceInvaders-v5 --start-mode 0 --first-mode 0 --last-mode 9 --seed 1
python run_experiments.py --algorithm prog-net --env ALE/SpaceInvaders-v5 --start-mode 0 --first-mode 0 --last-mode 9 --seed 1
python run_experiments.py --algorithm packnet --env ALE/SpaceInvaders-v5 --start-mode 0 --first-mode 0 --last-mode 9 --seed 1
python run_experiments.py --algorithm finetune --env ALE/SpaceInvaders-v5 --start-mode 0 --first-mode 0 --last-mode 9 --seed 1
```

Atari Freeway 完整序列命令示例：

```powershell
cd experiments\atari
python run_experiments.py --algorithm componet --env ALE/Freeway-v5 --start-mode 0 --first-mode 0 --last-mode 7 --seed 1
```

Meta-World 完整序列命令示例：

```powershell
cd experiments\meta-world
python run_experiments.py --algorithm simple --seed 1 --start-mode 0
python run_experiments.py --algorithm componet --seed 1 --start-mode 0
python run_experiments.py --algorithm prognet --seed 1 --start-mode 0
python run_experiments.py --algorithm packnet --seed 1 --start-mode 0
python run_experiments.py --algorithm finetune --seed 1 --start-mode 0
```

验收标准：

- 至少一个环境完成所有方法和多个 seeds。
- 能用处理脚本生成论文对应的 performance / transfer 表或图。
- 记录每个任务耗时、GPU 型号、显存、依赖版本和随机种子。
- 明确列出与论文结果的数值差异和可能原因。

可能风险：

- 完整实验非常昂贵，论文级设置约为每任务 `1e6` timesteps，且需要多 seeds。
- RL 结果高方差，单 seed 不能代表论文结论。
- 论文、README、代码在 Freeway 任务数和部分默认参数上需要继续核对。
- README 说默认 CLI 参数就是论文参数，但 `run_ppo.py` 默认环境是 `BreakoutNoFrameskip-v4`，复现 Atari 论文任务时必须显式指定 `--env-id=ALE/SpaceInvaders-v5` 或 `--env-id=ALE/Freeway-v5`。

