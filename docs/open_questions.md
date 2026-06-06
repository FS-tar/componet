# CompoNet 复现开放问题

说明：本文件已基于 `paper/self_composing_policies.pdf` 二次复核。这里仅保留论文没有完全解决、需要代码阅读、实验验证或导师决策的问题；PDF 已明确回答的内容不再列为开放问题。

## 1. PDF 已回答的问题

- Meta-World 任务序列：10 个任务重复两轮，共 20 个任务；任务名称和顺序在 Appendix D.1 给出。
- 论文级训练预算：每任务 `1M` timesteps。
- 随机种子数量：Table 1 结果为 10 random seeds 的均值和标准差。
- Atari success score 定义：Appendix D.4 定义为所有 8 个方法、10 seeds 最终 episodic return 平均值的 90%，并给出固定表 D.1。
- DINO 定位：Appendix A 是视觉 foundation model 表示的初步可行性分析，不是三组主实验的核心设置；主 Atari 实验使用 CNN encoder。

## 2. 仍需代码或数据确认的问题

- Freeway 任务数不一致：论文正文称 7 playing modes，Appendix D.3 描述到 mode 6；但 Appendix D.4 表 D.1b 和本地 `experiments/atari/task_utils.py` 使用 TASK/mode 0-7。复现时暂跟随附录表格和代码，但正式报告需解释该差异。
- Atari success score 处理差异：论文 D.4 写 90%，但本地 `experiments/atari/process_results.py` 的 `SETTINGS` 使用 `sc_percent=1.0`。需要确认官方 CSV 是否已预处理，或代码是否与论文文字存在偏差。
- Reference Transfer 复现细节：`transfer_matrix.py` / `transferer_matrix.py` 中 smoothing、插值和归一化实现需要与论文 Section 5.1 和 Appendix D.5 对齐。
- Atari `run_experiments.py` 参数：脚本要求 `--first-mode` 和 `--last-mode`，但当前代码未用它们控制范围；需要确认是否遗留参数。
- `prev_units` 路径规则：需要通过小规模实验确认 Atari 和 Meta-World 的保存目录与加载路径完全匹配。
- 本地 Python 环境：当前 shell 中直接运行 `python` 不可用，复现实验前需要确认虚拟环境或 Python 可执行路径。
- 官方数据路径：`data.tar.xz` 解压后的目录结构、CSV 列名和 `process_results.py` 默认参数是否完全匹配，需要实际解压后确认。

## 3. 需要问导师的问题

- 第一阶段复现优先选择 Atari 还是 Meta-World？Atari 安装可能更轻，Meta-World 的 success 指标更直接。
- smoke test 是否只要求验证训练管线、保存/加载和日志记录，不要求性能提升？
- 是否允许先使用仓库自带官方数据复现论文图表流程，再逐步做本地训练复现？
- 如果算力不足，是否可以接受两个任务的小规模 CompoNet 链路验证作为阶段性结果？
- 汇报时更关注 CompoNet 的机制、指标定义和代码理解，还是完整实验曲线复现？

## 4. 风险记录

- 强化学习结果高方差，单 seed smoke test 只能验证流程，不能证明论文结论。
- 完整实验成本高：每任务 `1M` timesteps，三组序列、多方法、10 seeds 会迅速放大计算量。
- Atari 依赖风险包括 Gymnasium/ALE、ROM、wrapper 版本和 Windows 环境兼容。
- Meta-World 依赖风险包括 MuJoCo、Metaworld 版本、Gymnasium API 和 Python 版本兼容。
- 大型输出目录如 `runs/`、`agents/`、`videos/`、解压后的数据不应提交到 git。

## Verification Notes

- 本文档已基于 `paper/self_composing_policies.pdf` 复核。
- 来自论文的内容：Meta-World 任务序列、训练预算、10 seeds、Atari success score、DINO 的附录定位、实验指标和主实验方法。
- 来自代码检查的内容：Freeway 代码使用 0-7；Atari `process_results.py` 使用 `sc_percent=1.0`；Atari 批量脚本无 `--no-run` 且未使用 `first-mode/last-mode` 控制范围；Meta-World 批量脚本有 `--no-run`。
- 仍需从代码或实验确认：官方 CSV 与处理脚本的匹配关系、保存/加载路径、依赖环境、smoke test 是否能跑通。
- 目前仍不确定：Freeway 7 vs 8 的正式复现口径；Atari success score 的论文文字与本地处理脚本差异是否影响复现结果。
