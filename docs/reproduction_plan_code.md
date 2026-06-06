# 从代码角度制定复现计划

本文档只规划代码层面的检查和 smoke test，不安装依赖，不运行训练，不修改算法代码。

## 1. 环境检查顺序

1. 阅读 `README.md`，确认官方把依赖分为 Atari 和 Meta-World 两组，并确认训练脚本都支持 `--help`。
2. 阅读 `experiments/atari/requirements.txt`，记录 Atari 需要 `torch==2.1.0`、`gymnasium[atari]==0.28.1`、`ale-py==0.8.1`、`stable-baselines3==2.0.0`、`tyro==0.5.10`、`tensorboard==2.11.2` 等。
3. 阅读 `experiments/meta-world/requirements.txt`，记录 Meta-World 需要 `metaworld` Git 依赖、`mujoco==2.3.7`、`gymnasium==0.29.1`、`torch==2.1.2`、`wandb==0.16.1` 等。
4. 只运行入口脚本的 `--help`，不运行训练，用于确认 tyro/argparse 参数名称和布尔参数写法。
5. 检查 `.gitignore`，当前已忽略 `*__pycache__*`、`*wandb*`、`*runs*`、`experiments/atari/data`、`experiments/meta-world/data`。
6. 检查训练脚本输出路径：`experiments/atari/run_ppo.py` 和 `experiments/meta-world/run_sac.py` 都会写 TensorBoard `runs/<run_name>`；设置 `--save-dir` 时会写模型目录。

## 2. 如何选择 Atari 或 Meta-World

建议先从 Atari 开始：

- `experiments/atari/run_ppo.py` 的参数更直接，任务序列在 `experiments/atari/task_utils.py` 中只是 Atari mode id。
- Atari 可以先用 `--model-type=cnn-simple`，不需要历史模型路径，也不需要 CompoNet previous units。
- Meta-World 的 `experiments/meta-world/run_sac.py` 依赖 `metaworld`、`mujoco` 和连续控制环境，安装和初始化风险更高。
- Meta-World 的 `--model-type=componet` 要求 `--prev-units` 至少有一个历史模型；从零开始 smoke test 应先用 `--model-type=simple`。

如果目标是尽快检查官方代码是否能启动，优先 Atari `cnn-simple`。如果目标是检查 SAC 代码路径，Meta-World 也应先用 `simple`，不要直接跑 `componet`。

## 3. 先运行 `--help` 的脚本

优先顺序：

1. `experiments/atari/run_ppo.py --help`：确认 PPO 训练参数、`--model-type`、`--total-timesteps`、`--num-envs`、`--num-steps`、`--save-dir`、`--cuda/--no-cuda` 等 tyro 写法。
2. `experiments/atari/test_agent.py --help`：确认评估参数、`--load`、`--mode`、`--num-episodes`、`--max-timesteps`、`--csv`。
3. `experiments/meta-world/run_sac.py --help`：确认 SAC 训练参数、`--model-type`、`--task-id`、`--total-timesteps`、`--learning-starts`、`--random-actions-end`、`--eval-every`、`--num-evals`。
4. `experiments/meta-world/test_agent.py --help`：确认评估参数、`--load`、`--task-id`、`--num-episodes`、`--csv`。
5. `experiments/meta-world/run_experiments.py --help`：确认 `--no-run`，可用于只打印批量命令。
6. `experiments/atari/run_experiments.py --help`：确认批量运行参数，但不要直接运行完整序列。

## 4. 最短 smoke test 设计

Atari 首选 smoke test 思路：

- 入口：`experiments/atari/run_ppo.py`
- 模型：`--model-type=cnn-simple`
- 环境：`--env-id=ALE/Freeway-v5` 或 `--env-id=ALE/SpaceInvaders-v5`
- 任务 mode：先用 `--mode=0`
- 时间步：把 `--total-timesteps` 设得很小
- 并行环境数：把 `--num-envs` 设得很小
- rollout 长度：把 `--num-steps` 设得很小
- 关闭外部记录：不加 `--track`，不加 `--capture-video`
- 保存：第一轮可不设置 `--save-dir`，避免生成模型文件；如果需要测试评估，再用临时 `--save-dir=agents_smoke`

Meta-World 首选 smoke test 思路：

- 入口：`experiments/meta-world/run_sac.py`
- 模型：`--model-type=simple`
- 任务：`--task-id=0`
- 时间步：把 `--total-timesteps` 设得很小
- 学习启动：把 `--learning-starts` 和 `--random-actions-end` 调小，否则极短 smoke test 可能只采样不训练
- replay buffer：可适当调小 `--buffer-size`
- 评估：把 `--num-evals` 调小
- 关闭外部记录：不加 `--track`，不加 `--capture-video`
- 保存：第一轮可不设置 `--save-dir`

CompoNet smoke test 应放在 baseline smoke test 之后，因为：

- Atari `experiments/atari/models/cnn_componet.py` 在后续任务需要 `--prev-units` 指向之前任务保存的 `actor.pt`、`encoder.pt`。
- Meta-World `experiments/meta-world/models/compo.py` 在 `run_sac.py` 中要求 `--prev-units` 非空。

## 5. 如何避免直接跑完整长实验

- 不直接运行 `experiments/atari/run_experiments.py`，因为它会按任务序列循环调用 `run_ppo.py`，且内部固定 `timesteps = int(1e6)`。
- Meta-World 可以先运行 `experiments/meta-world/run_experiments.py --no-run` 打印命令，但不执行训练。
- 直接调用单任务入口 `experiments/atari/run_ppo.py` 或 `experiments/meta-world/run_sac.py`，手动覆盖 `--total-timesteps` 等参数。
- 不加 `--track`，避免启动 Weights & Biases。
- 不加 `--capture-video`，避免生成视频目录。
- 第一轮不设置 `--save-dir`，避免生成 `.pt` 模型文件。
- 不解压 `experiments/atari/data.tar.xz` 或 `experiments/meta-world/data.tar.xz`，除非只是复现实验图表且已确认需要。

## 6. 可能很大的输出文件和目录

需要避免提交或后续加入 `.gitignore` 的输出：

- `runs/`：`experiments/atari/run_ppo.py` 和 `experiments/meta-world/run_sac.py` 的 TensorBoard event 输出。
- `wandb/`：使用 `--track` 时可能生成的 Weights & Biases 本地日志。
- `videos/`：使用 `--capture-video` 或 render 时可能生成的视频。
- `agents/`：`run_experiments.py` 默认使用的模型保存目录。
- `agents_smoke/`：如果为 smoke test 单独保存模型，建议使用这种临时目录并忽略。
- `*.pt`：模型权重，例如 Atari 的 `actor.pt`、`crititc.pt`、`encoder.pt`，Meta-World 的 `model.pt`、`net_mean.pt`、`net_logstd.pt`。
- `events.out.tfevents.*`：TensorBoard event 文件。
- `experiments/atari/data/` 和 `experiments/meta-world/data/`：解压后的数据目录，当前 `.gitignore` 已覆盖。
- `experiments/atari/data.tar.xz` 和 `experiments/meta-world/data.tar.xz` 已在仓库中存在，不应重复生成或替换。

当前 `.gitignore` 已忽略 `*wandb*`、`*runs*` 和两个实验数据目录，但没有显式忽略 `agents/`、`videos/`、`*.pt`、`agents_smoke/`。本次任务不修改 `.gitignore`，只记录风险。

## 7. 最适合作为第一入口的脚本

- 阅读入口：`README.md`
- Atari 代码入口：`experiments/atari/run_ppo.py`
- Atari 任务序列入口：`experiments/atari/task_utils.py`
- Atari 最简单模型入口：`experiments/atari/models/cnn_simple.py`
- Atari CompoNet 模型入口：`experiments/atari/models/cnn_componet.py`
- Meta-World 代码入口：`experiments/meta-world/run_sac.py`
- Meta-World 任务序列入口：`experiments/meta-world/tasks.py`
- Meta-World 最简单模型入口：`experiments/meta-world/models/simple.py`
- Meta-World CompoNet 模型入口：`experiments/meta-world/models/compo.py`

第一轮实际 smoke test 建议顺序：

1. `experiments/atari/run_ppo.py --help`
2. `experiments/atari/run_ppo.py` 的极小 `cnn-simple` 单任务运行
3. 如保存了模型，再看 `experiments/atari/test_agent.py --help`
4. 再评估保存的 Atari 模型
5. Meta-World 等 Atari 路径确认后再检查
