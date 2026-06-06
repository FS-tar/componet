# 代码阅读后未决问题

本文档记录只通过代码阅读还不能完全确认的问题，后续需要 `--help`、smoke test 或论文对齐来确认。

## 1. 从代码看还不清楚的问题

- `experiments/meta-world/test_agent.py` 当前只在 `if method in ["simple", "finetune"]:` 分支中加载 `SimpleAgent`，但文件顶部导入了 `CompoNetAgent`、`PackNetAgent`、`ProgressiveNetAgent`。需要确认官方是否只用该脚本评估 simple/finetune，还是 `componet/prognet/packnet` 的评估加载逻辑遗漏了。
- `experiments/meta-world/models/compo.py` 的 `CompoNetAgent.load()` 中出现 `prevs_paths` 变量名，但函数参数是 `prev_paths`；还把 `net_mean = torch.load(f"{dirname}/net_logstd.pt", ...)` 指向了 `net_logstd.pt`。这些可能是未使用路径中的 typo，需要通过实际评估或加载 smoke test 确认。
- `experiments/atari/models/cnn_componet.py` 保存 critic 的文件名是 `crititc.pt`，加载时也使用同样拼写。虽然能自洽，但需要记录为官方代码中的固定文件名，避免手动寻找 `critic.pt`。
- `experiments/atari/run_experiments.py` 内部固定 `timesteps = int(1e6)`，不能直接作为短 smoke test 入口，除非修改代码；本项目当前规则不应修改官方训练脚本。
- `experiments/meta-world/run_experiments.py` 有 `--no-run`，但 `experiments/atari/run_experiments.py` 没有类似参数。Atari 批量命令只能读代码或运行 `--help`，不应直接启动。
- `experiments/meta-world/transferer_matrix.py` 文件名是 `transferer_matrix.py`，不是常见的 `transfer_matrix.py`。后续写命令时要使用实际文件名。

## 2. 需要运行 `--help` 才能确认的问题

- `experiments/atari/run_ppo.py` 使用 tyro dataclass，需通过 `--help` 确认 CLI 参数实际写法，例如 `--model-type`、`--total-timesteps`、`--num-envs`、`--num-steps`、`--no-cuda`、`--componet-finetune-encoder`。
- `experiments/atari/run_ppo.py` 的 `prev_units: Tuple[pathlib.Path, ...]` 需要通过 `--help` 确认多路径参数写法，尤其是 CompoNet/ProgressiveNet 后续任务的 `--prev-units path1 path2 ...`。
- `experiments/meta-world/run_sac.py` 使用 tyro dataclass，需确认布尔参数写法，例如 `--track/--no-track`、`--cuda/--no-cuda`、`--autotune/--no-autotune`。
- `experiments/meta-world/run_sac.py` 的 `--prev-units` 多路径写法需要确认。
- `experiments/atari/test_agent.py` 和 `experiments/meta-world/test_agent.py` 使用 argparse，需确认评估时 `--csv` 路径是否覆盖或追加，以及 `--render` 是否会要求 GUI。
- `experiments/meta-world/run_experiments.py --no-run` 需要确认打印出的命令是否包含足够参数，是否仍默认写 `agents/`。

## 3. 需要跑 smoke test 才能确认的问题

- Atari 环境是否能创建：`experiments/atari/run_ppo.py` 调用 `gym.make(env_id, mode=mode)`，需要确认本机是否已安装 ALE ROM，以及 `ALE/Freeway-v5` 和 `ALE/SpaceInvaders-v5` 是否可用。
- Atari wrappers 是否兼容：`experiments/atari/run_ppo.py` 使用 `stable_baselines3.common.atari_wrappers` 中的 `NoopResetEnv`、`MaxAndSkipEnv`、`EpisodicLifeEnv`、`FireResetEnv`、`ClipRewardEnv`，需要确认与当前 gymnasium/ALE 版本兼容。
- Meta-World 环境是否能创建：`experiments/meta-world/tasks.py` 从 `metaworld.envs import ALL_V2_ENVIRONMENTS_GOAL_OBSERVABLE`，需要确认 metaworld Git 依赖、MuJoCo 和渲染/非渲染模式可用。
- TensorBoard 日志是否正常：`experiments/atari/run_ppo.py` 和 `experiments/meta-world/run_sac.py` 都会创建 `SummaryWriter(f"runs/{run_name}")`，需要确认短运行能正常写 event 文件。
- 极短 `total_timesteps` 是否会产生至少一次 PPO 更新：Atari 中 `num_iterations = total_timesteps // (num_envs * num_steps)`，如果 `total_timesteps` 小于 batch size，循环不会执行。
- 极短 `total_timesteps` 是否会产生 SAC 更新：Meta-World 中只有 `global_step > learning_starts` 后才训练；如果 smoke test 过短，可能只测试环境交互，不测试优化器路径。
- 保存和加载是否匹配：如果设置 `--save-dir`，需要确认 `experiments/atari/test_agent.py` 和 `experiments/meta-world/test_agent.py` 能按保存目录名解析 method、task/mode、seed。

## 4. 代码和论文可能需要对齐的问题

- 论文中的 CompoNet attention 结构需要和 `componet/impl.py` 中的 output attention head、input attention head、internal policy、最终 `out_head + logits` 对齐。
- 论文中的“历史策略模块冻结”需要和 `componet/impl.py` 中 `previous_units` 的 `eval()` 与 `requires_grad=False` 对齐。
- Atari 论文实验中的 SpaceInvaders/Freeway 任务序列需要和 `experiments/atari/task_utils.py` 中的 mode 列表对齐。
- Meta-World 论文实验的 20 任务序列需要和 `experiments/meta-world/tasks.py` 中 `tasks = single_tasks + single_tasks` 对齐。
- 论文中的 forward transfer、final performance、forgetting 指标需要和 `experiments/atari/process_results.py`、`experiments/meta-world/process_results.py` 中的计算方式对齐。
- 论文中的 transfer matrix 需要和 `experiments/atari/transfer_matrix.py`、`experiments/meta-world/transferer_matrix.py` 的计算和 baseline 选择对齐。
- 论文中 attention/match 的可视化指标需要和 `experiments/atari/models/cnn_componet.py`、`experiments/meta-world/models/compo.py` 写入 TensorBoard 的 `charts/att_in_*`、`charts/att_out_*`、`charts/out_matches_*`、`charts/dist_*` 对齐。

## 5. 环境安装可能遇到的风险

- Atari 依赖风险：`experiments/atari/requirements.txt` 同时包含 `gym==0.23.1` 和 `gymnasium[atari]==0.28.1`，还依赖 `ale-py`、`autorom` 和 Atari ROM license，可能出现 ROM 不存在或 wrapper 版本不兼容问题。
- Meta-World 依赖风险：`experiments/meta-world/requirements.txt` 使用 Git URL 安装 `metaworld`，需要网络和 Git；本项目规则要求不要擅自安装依赖。
- MuJoCo 风险：Meta-World 依赖 `mujoco==2.3.7`，可能遇到本机图形、动态库、渲染后端或 Windows 兼容问题。
- PyTorch 版本风险：Atari 要求 `torch==2.1.0`，Meta-World 要求 `torch==2.1.2`，两个实验目录的版本不完全一致，最好使用分开的环境。
- CUDA 依赖风险：`experiments/meta-world/requirements.txt` 固定了多个 `nvidia-cu12` 包，Windows 或 CPU-only 环境可能不适合直接照装。
- DINO 路径风险：`experiments/atari/models/dino_encoder.py` 会引入 DINO 模型相关依赖/下载风险，第一轮 smoke test 不应选择 `--model-type=dino-simple`。
- Weights & Biases 风险：训练脚本只有加 `--track` 才会启用 wandb；smoke test 应避免 `--track`，否则可能要求登录或联网。
