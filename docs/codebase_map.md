# 官方代码结构地图

本文档只从代码阅读角度记录官方仓库结构，不修改算法实现，不安装依赖，不运行训练。

## 1. 仓库整体结构

- `README.md`：官方说明文件，给出论文信息、仓库结构、依赖文件位置和复现实验入口。README 明确说明 PPO/SAC 脚本基于 CleanRL。
- `AGENTS.md`：本地复现与学习规则，要求把代码结构说明放在 `docs/codebase_map.md`，并优先理解官方实现。
- `paper/self_composing_policies.pdf`：论文 PDF，用于把代码实现和论文方法对齐。
- `componet/`：CompoNet 核心结构实现。主要代码在 `componet/impl.py`，`componet/__init__.py` 只导出核心类。
- `experiments/atari/`：Atari SpaceInvaders 和 Freeway 序列实验，训练入口是 `experiments/atari/run_ppo.py`，批量运行入口是 `experiments/atari/run_experiments.py`。
- `experiments/atari/models/`：Atari PPO agent 的模型实现，包括 CompoNet、baseline、finetune、ProgressiveNet、PackNet 和 DINO/CNN 编码器。
- `experiments/meta-world/`：Meta-World 连续控制任务实验，训练入口是 `experiments/meta-world/run_sac.py`，批量运行入口是 `experiments/meta-world/run_experiments.py`。
- `experiments/meta-world/models/`：Meta-World SAC actor 模型实现，包括 CompoNet、simple、finetune、ProgressiveNet、PackNet。
- `utils/`：跨脚本工具，目前主要是绘图样式 `utils/plt_style.py`。

## 2. `componet/` 核心文件

- `componet/__init__.py`：从 `componet/impl.py` 导出 `CompoNet` 和 `FirstModuleWrapper`，供实验目录通过 `from componet import ...` 使用。
- `componet/impl.py`：官方 CompoNet 架构的核心实现。
  - `get_position_encoding(seq_len, d, n=10_000)`：生成 attention 中使用的位置编码，给不同历史 module 输出加入顺序信息。
  - `logit2prob(logits)`：用 softmax 把 logits 转成概率向量，Atari 离散动作策略会用到。
  - `Identity`：可序列化的恒等变换，避免 `torch.save` 不能 pickle lambda 的问题。
  - `CompoNet`：核心模块。接收历史策略模块 `previous_units`、当前任务 internal policy、输入维度、隐藏维度和输出维度。
  - `CompoNet._forward_headout()`：实现 output attention head，用当前状态表示查询历史策略输出，得到历史策略输出的加权组合。
  - `CompoNet._get_internal_policy()`：实现 input attention head，把历史输出和 output head 结果组合后，与当前状态拼接，送入当前任务 internal policy。
  - `CompoNet.forward()`：执行完整组合逻辑。当前模块会先调用冻结的历史模块得到 `phi`，然后计算 output head、internal policy、最终输出，并可返回 attention、encoder 输出、中间策略输出等诊断信息。
  - `FirstModuleWrapper`：第一任务没有历史 CompoNet module 时使用的包装器。它把普通 PyTorch 模型包装成与 CompoNet 后续模块兼容的 `(policy_output, phi)` 形式。
  - 历史模块冻结逻辑：`CompoNet.__init__()` 中对 `previous_units` 设置 `eval()`，并把参数 `requires_grad=False`，防止训练当前任务时更新旧任务模块。

## 3. `experiments/atari/` 核心脚本

- `experiments/atari/run_ppo.py`：Atari PPO 主训练入口。它定义 tyro dataclass 参数 `Args`，创建 Atari 环境，选择模型类型，执行 PPO rollout、GAE、policy/value loss 更新，并写入 TensorBoard `runs/`。如果设置 `--save-dir`，会保存 agent 到对应目录。
- `experiments/atari/run_experiments.py`：批量实验脚本。根据 `experiments/atari/task_utils.py` 中的任务序列和 `--algorithm` 拼接多任务训练命令，依次调用 `python3 run_ppo.py ...`。
- `experiments/atari/task_utils.py`：定义 Atari 任务序列。`TASKS["ALE/SpaceInvaders-v5"]` 是 mode 0 到 9，`TASKS["ALE/Freeway-v5"]` 是 mode 0 到 7；还提供模型名解析和跨 mode 路径替换。
- `experiments/atari/test_agent.py`：Atari 训练后评估入口。根据保存目录名解析环境、训练 mode、算法和 seed，加载模型后运行若干 episode，可选写入 CSV。
- `experiments/atari/process_results.py`：处理 TensorBoard/CSV 结果，计算 success、forward transfer、final performance、遗忘指标，并生成汇总 CSV 和图。
- `experiments/atari/transfer_matrix.py`：从 TensorBoard runs 解析标量，计算 SpaceInvaders/Freeway 的 transfer matrix 并画图。
- `experiments/atari/plot_ablation_input_head.py`：绘制 input attention head ablation 相关曲线和 attention 图。
- `experiments/atari/plot_ablation_output_head.py`：绘制 output attention head ablation 结果。
- `experiments/atari/plot_arch_val.py`：绘制结构验证实验结果，包括 return、matches、attention。
- `experiments/atari/plot_dino_vs_cnn.py`：绘制 DINO 编码器与 CNN 编码器比较结果。

## 4. `experiments/atari/models/` 核心文件

- `experiments/atari/models/__init__.py`：导出 Atari 训练脚本中使用的 agent 类。
- `experiments/atari/models/cnn_componet.py`：Atari CompoNet agent。它把 `CnnEncoder`、critic、internal policy 和 `componet/impl.py` 中的 `CompoNet` 组合起来。第一任务使用 `FirstModuleWrapper`，后续任务加载历史 `actor.pt` 作为 `previous_units`。
- `experiments/atari/models/cnn_encoder.py`：Atari CNN 图像编码器，把 frame stack 图像编码到 hidden feature。
- `experiments/atari/models/cnn_simple.py`：普通 CNN PPO agent baseline，也是 finetune 的基础模型。
- `experiments/atari/models/dino_encoder.py`：DINO 图像编码器封装。
- `experiments/atari/models/dino_simple.py`：使用 DINO encoder 的 PPO agent。
- `experiments/atari/models/progressive_net.py`：Atari ProgressiveNet baseline。
- `experiments/atari/models/packnet.py`：Atari PackNet baseline，包括 pruning、mask view 和 retraining 逻辑。

## 5. `experiments/meta-world/` 核心脚本

- `experiments/meta-world/run_sac.py`：Meta-World SAC 主训练入口。它定义 tyro dataclass 参数 `Args`，创建 Meta-World 环境，选择 actor 模型，定义 SAC 的 actor、Q network、replay buffer、entropy tuning、target update 和评估逻辑。
- `experiments/meta-world/run_experiments.py`：批量实验脚本。根据算法和 `--start-mode` 拼接命令调用 `python3 run_sac.py ...`；它有 `--no-run`，适合先检查将要执行的命令。
- `experiments/meta-world/tasks.py`：定义 Meta-World 任务序列。`single_tasks` 有 10 个任务，`tasks = single_tasks + single_tasks` 扩展成 20 个任务；`get_task()` 负责创建具体环境。
- `experiments/meta-world/test_agent.py`：Meta-World 评估入口。当前代码显式处理 `simple/finetune` 加载路径，其他算法加载路径需要进一步确认。
- `experiments/meta-world/process_results.py`：处理 TensorBoard runs 和评估 CSV，计算 performance、forward transfer、forgetting，并输出汇总 CSV 和图。
- `experiments/meta-world/transferer_matrix.py`：计算并绘制 Meta-World transfer matrix。文件名是 `transferer_matrix.py`，不是 `transfer_matrix.py`。
- `experiments/meta-world/benchmarking.py`：比较 CompoNet 与 ProgressiveNet 在任务数量增加时的参数量、运行时间、内存等，并可绘图。

## 6. `experiments/meta-world/models/` 核心文件

- `experiments/meta-world/models/__init__.py`：导出 Meta-World SAC actor 侧模型。
- `experiments/meta-world/models/compo.py`：Meta-World CompoNet actor 模型。`CompoNetAgent` 用 `CompoNet` 生成 action mean，用单独网络 `net_logstd` 生成 log std。
- `experiments/meta-world/models/simple.py`：普通 MLP actor baseline，也用于 finetune 加载。
- `experiments/meta-world/models/shared_arch.py`：SAC Q network 和部分模型共享的 MLP hidden feature 构造函数。
- `experiments/meta-world/models/prognet.py`：Meta-World ProgressiveNet baseline。
- `experiments/meta-world/models/packnet.py`：Meta-World PackNet baseline，包括 mask、pruning 和任务 view。

## 7. CompoNet 核心结构在哪里

- 通用核心结构：`componet/impl.py`
- Atari 调用 CompoNet：`experiments/atari/models/cnn_componet.py`
- Meta-World 调用 CompoNet：`experiments/meta-world/models/compo.py`
- CompoNet/ProgressiveNet benchmark：`experiments/meta-world/benchmarking.py`

## 8. PPO 在哪里实现或调用

- PPO 主实现：`experiments/atari/run_ppo.py`
- PPO agent 模型：`experiments/atari/models/cnn_simple.py`、`experiments/atari/models/cnn_componet.py`、`experiments/atari/models/dino_simple.py`、`experiments/atari/models/progressive_net.py`、`experiments/atari/models/packnet.py`
- PPO 批量调用：`experiments/atari/run_experiments.py`
- PPO 评估：`experiments/atari/test_agent.py`

## 9. SAC 在哪里实现或调用

- SAC 主实现：`experiments/meta-world/run_sac.py`
- SAC actor 模型：`experiments/meta-world/models/simple.py`、`experiments/meta-world/models/compo.py`、`experiments/meta-world/models/prognet.py`、`experiments/meta-world/models/packnet.py`
- SAC 批量调用：`experiments/meta-world/run_experiments.py`
- SAC 评估：`experiments/meta-world/test_agent.py`

## 10. 任务序列在哪里

- Atari：`experiments/atari/task_utils.py`
  - `ALE/SpaceInvaders-v5`：`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`
  - `ALE/Freeway-v5`：`[0, 1, 2, 3, 4, 5, 6, 7]`
- Meta-World：`experiments/meta-world/tasks.py`
  - 10 个 `single_tasks`
  - `tasks = single_tasks + single_tasks`，总计 20 个任务 id

## 11. 训练入口在哪里

- Atari 单次训练：`experiments/atari/run_ppo.py`
- Atari 批量训练：`experiments/atari/run_experiments.py`
- Meta-World 单次训练：`experiments/meta-world/run_sac.py`
- Meta-World 批量训练：`experiments/meta-world/run_experiments.py`

## 12. 评估入口在哪里

- Atari：`experiments/atari/test_agent.py`
- Meta-World：`experiments/meta-world/test_agent.py`
- Meta-World 训练中也会评估：`experiments/meta-world/run_sac.py` 中的 `eval_agent()`

## 13. 结果处理和画图在哪里

- Atari 汇总处理：`experiments/atari/process_results.py`
- Atari transfer matrix：`experiments/atari/transfer_matrix.py`
- Atari ablation/对比图：`experiments/atari/plot_ablation_input_head.py`、`experiments/atari/plot_ablation_output_head.py`、`experiments/atari/plot_arch_val.py`、`experiments/atari/plot_dino_vs_cnn.py`
- Meta-World 汇总处理：`experiments/meta-world/process_results.py`
- Meta-World transfer matrix：`experiments/meta-world/transferer_matrix.py`
- Meta-World benchmark 图：`experiments/meta-world/benchmarking.py`
- 绘图样式：`utils/plt_style.py`

## 14. 配置文件在哪里

本仓库没有单独的 YAML/JSON 配置文件。主要配置来自脚本 CLI 参数：

- Atari PPO 参数：`experiments/atari/run_ppo.py` 的 `Args`
- Atari 批量实验参数：`experiments/atari/run_experiments.py`
- Atari 评估参数：`experiments/atari/test_agent.py`
- Meta-World SAC 参数：`experiments/meta-world/run_sac.py` 的 `Args`
- Meta-World 批量实验参数：`experiments/meta-world/run_experiments.py`
- Meta-World 评估参数：`experiments/meta-world/test_agent.py`

## 15. 依赖文件在哪里

- Atari 依赖：`experiments/atari/requirements.txt`
- Meta-World 依赖：`experiments/meta-world/requirements.txt`

注意：`experiments/meta-world/requirements.txt` 包含 `metaworld @ git+https://github.com/Farama-Foundation/Metaworld.git@...`、`mujoco` 和 CUDA 相关 PyTorch 包，环境风险比 Atari 更高。

## 16. smoke test 优先看哪些文件

优先阅读顺序：

1. `README.md`：确认官方推荐入口和依赖分组。
2. `experiments/atari/run_ppo.py`：确认 PPO 参数、默认输出目录、最小步数参数。
3. `experiments/atari/task_utils.py`：确认 Atari mode 序列。
4. `experiments/atari/models/cnn_simple.py`：先用最简单 CNN baseline 降低 CompoNet 历史模型依赖。
5. `experiments/meta-world/run_sac.py`：确认 SAC 参数、replay buffer、评估和保存逻辑。
6. `experiments/meta-world/tasks.py`：确认 Meta-World 任务 id 到环境名的映射。
7. `experiments/atari/test_agent.py` 和 `experiments/meta-world/test_agent.py`：确认训练后评估命令和 CSV 输出格式。

第一轮 smoke test 不应直接从 `experiments/atari/run_experiments.py` 启动完整任务序列，因为它会循环调用长训练。Meta-World 的 `experiments/meta-world/run_experiments.py --no-run` 可用于先打印命令，但实际最小训练 smoke test 仍应直接调用 `run_sac.py`。
