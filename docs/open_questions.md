# CompoNet 复现开放问题

说明：当前本地仓库没有 `paper/self_composing_policies.pdf`。以下问题基于官方论文页面、本地 README 和代码初步阅读整理，后续补齐 PDF 后需要再次核对。

## 1. 论文中没有说清楚但复现需要知道的问题

- Freeway 任务数不一致：论文规划里提到 Freeway modes 0-6，但本地 `experiments/atari/task_utils.py` 中 `ALE/Freeway-v5` 是 `[0, 1, 2, 3, 4, 5, 6, 7]`，共 8 个 mode。需要确认论文最终实验到底用了 7 个还是 8 个。
- HTML 版本中的部分附录表格/超参显示可能不完整，需要用 PDF 原文核对 PPO、SAC、CompoNet、PackNet、ProgressiveNet 的完整超参。
- 论文如何严格定义 Atari success score，需要与 `experiments/atari/process_results.py` 中由 episodic return 阈值转换 success 的实现逐项核对。
- Reference Transfer 的计算是否完全对应代码里的 `transfer_matrix.py` / `transferer_matrix.py`，尤其是 smoothing window、插值和面积归一化。
- 论文实验中的每个 seed 列表、训练硬件、运行时长是否有更精确记录。
- DINO encoder 相关实验是否属于主复现目标，还是只作为架构/表示 ablation。

## 2. 需要从代码里确认的问题

- Atari 批量脚本对 CompoNet 自动添加 `--componet-finetune-encoder`，需要确认论文主实验是否全部使用该设置。
- Atari `run_experiments.py` 接收 `--first-mode` 和 `--last-mode`，但当前脚本主体主要用 `--start-mode` 和 `TASKS[env]` 序列，似乎没有实际使用 `first-mode/last-mode` 控制范围，需要进一步确认是否是遗留参数。
- `run_ppo.py` 默认 `env_id` 是 `BreakoutNoFrameskip-v4`，README 又说默认 CLI 参数是论文设置。实际复现 SpaceInvaders/Freeway 时必须显式传 `--env-id`，这应记录为 README 与脚本默认值的差异。
- CompoNet 是否只作用于 actor：Meta-World `run_sac.py` 中 actor 使用 CRL 模型，Q 网络看起来每次从头初始化；Atari agent 里 actor/critic 具体共享关系还需读 `experiments/atari/models/*` 进一步确认。
- `prev_units` 路径命名必须与 `run_name` 一致。Atari run name 是 `{env_id}_{mode}__{model_type}__run_ppo__{seed}`，Meta-World 是 `task_{task_id}__{model_type}__run_sac__{seed}`，需要在实验日志中记录每次保存路径。
- PackNet 在 Atari 需要 `--total-task-num`，Meta-World 代码中固定传 `total_task_num=20`，需要确认论文中是否一致。
- `process_results.py` 的输入有两类：官方 CSV 数据和本地 TensorBoard runs。每个图表到底从哪个脚本和哪种数据生成，需要建立代码地图。

## 3. 需要问导师的问题

- 第一阶段复现优先选择 Atari 还是 Meta-World？Atari 环境安装可能更轻，但 Meta-World 的 success 指标更直接。
- smoke test 是否只要求验证训练管线、保存/加载和日志记录，不要求性能提升？
- 是否允许先使用仓库自带 `data.tar.xz` 复现论文图表流程，再逐步进行本地训练复现？
- 如果算力不足，是否可以接受 Level 3 的小规模正式实验作为课程/组会阶段性结果？
- 学术讨论中更关注 CompoNet 的方法机制、指标定义，还是更关注能否完整复现实验曲线？
- 是否需要把 ProgressiveNet、PackNet 的理论对比单独整理成给导师看的讲解文档？

## 4. 随机性、算力和依赖版本风险

- 强化学习结果高方差。论文使用多 seed 统计，单 seed 的 smoke test 或小规模实验只能验证流程，不能证明论文结论。
- 完整实验成本高。默认训练是 `1e6` timesteps/task，Meta-World 20 个 task，SpaceInvaders 10 个 mode，Freeway 任务数还需核对；多方法多 seed 会迅速放大总耗时。
- 论文计划中估计完整设置每任务约 1.5-3 小时且需要 GPU；CPU 只适合 Level 1/2 的管线检查。
- Atari 依赖风险包括 `gymnasium`、`ale-py`、ROM 授权/安装、`stable-baselines3` wrapper 版本差异。
- Meta-World 依赖风险包括 `metaworld`、MuJoCo、Gymnasium API、Python 版本兼容性。
- CUDA、cuDNN deterministic 设置、不同 GPU 型号和 PyTorch 版本都会影响速度和少量数值差异。
- TensorBoard scalar 名称和日志目录结构会影响 `process_results.py` 能否正确聚合。
- 大型输出目录如 `runs/`、`agents/`、`videos/`、解压后的大型数据不应提交到 git，只在 `docs/experiment_log.md` 记录路径和摘要。

