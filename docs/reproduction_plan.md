# CompoNet 复现规划

说明：本规划已基于 `paper/self_composing_policies.pdf` 二次复核，并结合本地实验脚本做可执行性检查。本文只规划复现路线，不要求提交 `agents/`、`runs/`、`videos/`、checkpoint 或解压后的数据。

## 1. 论文实验设置

论文完整实验不是 smoke test，而是每个任务 `1M` timesteps、10 random seeds 的 CRL 评估。

- Meta-World：10 个任务重复两轮，共 20 个任务；使用 SAC；状态是 39 维连续向量，动作是 4 维连续向量。
- SpaceInvaders：`ALE/SpaceInvaders-v5`，正文和代码均对应 10 个 modes；使用 CNN encoder + PPO。
- Freeway：正文称 7 个 playing modes，Appendix D.3 描述到 mode 6；但 Appendix D.4 表 D.1b 和本地代码使用 TASK/mode 0-7。复现实操暂按代码和附录表格使用 0-7，同时在报告中保留不一致说明。
- 对比方法：Baseline、FT-1、FT-N、ProgressiveNet、PackNet、CompoNet。
- 指标：Average Performance、Forward Transfer、Reference forward Transfer。Atari success score 按论文 D.4 是所有 8 个方法、10 seeds 最终 episodic return 平均值的 90%。

Appendix E 需要作为超参核对依据，而不是只依赖 README 的“默认 CLI 参数即论文参数”。关键值包括 Meta-World/SAC 的 hidden dimension `256`、batch size `128`、buffer size `1e6`、random actions `1e4`、learning starts `5e3`；Atari/PPO 的 hidden dimension `512`、learning rate `2.5e-4`、8 parallel envs、batch size `1024`、rollout steps `128`。

## 2. Level 1: 环境与 CLI 只读检查

目标：确认本地能找到 Python、依赖入口和脚本参数，不启动训练。

先执行：

```powershell
git branch --show-current
git status
pwd
where.exe python
py --version
python --version
Get-Content experiments\atari\requirements.txt
Get-Content experiments\meta-world\requirements.txt
```

然后只运行 help：

```powershell
cd experiments\atari
python run_ppo.py --help
cd ..\meta-world
python run_sac.py --help
python run_experiments.py --algorithm componet --seed 1 --start-mode 0 --no-run
```

注意：Meta-World 的 `run_experiments.py` 支持 `--no-run`，可以只打印命令；Atari 的 `run_experiments.py` 不支持 `--no-run`，不要在 Level 1 运行 Atari 批量脚本。

验收标准：

- 记录实际可用的 Python 可执行名或虚拟环境路径。
- `run_ppo.py --help` 和 `run_sac.py --help` 能展示参数，或能定位缺失依赖。
- 不启动 `1M` timesteps 的训练。

## 3. Level 2: 最短 smoke test

目标：验证环境创建、模型初始化、日志写入和保存/加载链路。smoke test 不是论文设置，不用于声称复现论文数值。

Atari 单任务 smoke test 候选：

```powershell
cd experiments\atari
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=0 --total-timesteps=1024 --num-envs=1 --num-steps=32 --num-minibatches=1 --cuda=False
```

Meta-World 单任务 smoke test 候选：

```powershell
cd experiments\meta-world
python run_sac.py --model-type=simple --task-id=0 --total-timesteps=1000 --learning-starts=100 --random-actions-end=200 --cuda=False
```

验收标准：

- 只要求管线跑通，不要求性能提升。
- 记录命令、环境、输出、错误和结果到 `docs/experiment_log.md`。
- 如果失败，只修最可能原因后重试。

## 4. Level 3: 最小 CompoNet 链路验证

目标：在两个任务上验证 baseline、保存路径、`prev_units` 加载和 CompoNet 训练入口。该阶段仍不是论文级复现。

Atari 候选链路：

```powershell
cd experiments\atari
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=0 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents
python run_ppo.py --model-type=cnn-componet --env-id=ALE/Freeway-v5 --mode=1 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents --prev-units agents/ALE-Freeway-v5_0__cnn-simple__run_ppo__1 --componet-finetune-encoder
python run_ppo.py --model-type=cnn-simple --env-id=ALE/Freeway-v5 --mode=1 --seed=1 --total-timesteps=10000 --num-envs=1 --num-steps=64 --num-minibatches=1 --cuda=False --save-dir=agents
```

Meta-World 候选链路：

```powershell
cd experiments\meta-world
python run_sac.py --model-type=simple --task-id=0 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents
python run_sac.py --model-type=componet --task-id=1 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents --prev-units agents/task_0__simple__run_sac__1
python run_sac.py --model-type=simple --task-id=1 --seed=1 --total-timesteps=10000 --learning-starts=1000 --random-actions-end=1000 --cuda=False --save-dir=agents
```

验收标准：

- 第一任务模型能保存。
- 第二任务 CompoNet 能加载第一任务模型。
- baseline 与 CompoNet 都能写 TensorBoard。
- `agents/` 和 `runs/` 不提交到 git。

## 5. Level 4: 官方数据与指标处理

目标：优先用仓库自带压缩数据跑通论文图表处理流程，再考虑本地训练结果。

Atari：

```powershell
cd experiments\atari
python process_results.py --data-dir=data/envs/Freeway --eval-results=data/eval_results.csv
python process_results.py --data-dir=data/envs/SpaceInvaders --eval-results=data/eval_results.csv
```

Meta-World：

```powershell
cd experiments\meta-world
python process_results.py --runs-dir=runs --save-csv=data/agg_results.csv --eval-csv=data/eval_results.csv
```

复核重点：

- Atari 论文 D.4 的 90% success score 与本地 `process_results.py` 的 `sc_percent=1.0` 差异。
- `transfer_matrix.py` / `transferer_matrix.py` 的 smoothing、插值和面积归一化是否对应论文 Section 5.1 与 Appendix D.5。
- 官方 CSV 与本地 TensorBoard runs 的输入结构是否一致。

## 6. Level 5: 论文级完整复现

只有在 Level 1-4 都跑通、依赖和算力允许后，才考虑完整复现。

Atari 批量脚本风险：

- `experiments/atari/run_experiments.py` 没有 `--no-run`，运行即启动训练。
- 它要求 `--first-mode` 和 `--last-mode`，但当前代码未实际使用这两个参数控制范围，而是从 `--start-mode` 在 `TASKS[env]` 中的位置运行到序列末尾。
- 因此完整 Atari 实验前，应先手动拆成单条命令，确认每条命令的 `--env-id`、`--mode`、`--prev-units` 和保存路径。

Meta-World 批量脚本风险：

- 非 `simple` / `packnet` / `prognet` 算法在 `--start-mode 0` 时会自动从 task 1 开始，因为 CompoNet/finetune 需要已有前序模型。
- 完整序列共 20 个 task，论文级设置是每任务 `1M` timesteps、10 seeds。

## Verification Notes

- 本文档已基于 `paper/self_composing_policies.pdf` 复核。
- 来自论文的内容：三组任务序列、SAC/PPO、`1M` timesteps/task、10 random seeds、指标定义、Appendix D/E 的任务、success score 和超参。
- 来自代码检查的内容：Atari `run_experiments.py` 无 `--no-run` 且未使用 `first-mode/last-mode` 控制范围；Meta-World 批量脚本支持 `--no-run`；Freeway 代码 modes 为 0-7。
- 仍需从代码或实验确认：本地环境可用 Python 路径、依赖安装状态、模型保存路径、官方 CSV 解压后的实际目录结构。
- 目前仍不确定：Freeway 论文正文 7 modes 与 Appendix D.4/代码 8 tasks 的正式解释口径；Atari `process_results.py` 与论文 D.4 指标计算差异是否来自官方数据预处理约定。
