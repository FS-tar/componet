# CompoNet 论文理解笔记

论文：Self-Composing Policies for Scalable Continual Reinforcement Learning。

说明：本文档已重新基于本地 `paper/self_composing_policies.pdf` 复核。PDF 共 29 页，论文发表信息为 ICML 2024；本地 PDF 首页同时显示 arXiv `2506.14811v1`，日期为 2025-06-04。以下内容优先依据论文正文和附录；涉及本地代码的内容单独标注为代码确认点。

*Composition Network 会组合旧策略的新策略网络

## 1. 论文要解决的问题

论文关注 Continual Reinforcement Learning (CRL)：智能体按顺序学习一串任务，每个任务只有有限交互预算，不能把所有任务重新联合训练。理想的 CRL agent 应该能复用旧知识来加速新任务学习，同时避免学习新任务时破坏旧任务能力。

论文指出，深度强化学习中的持续学习面临两个核心现象：

- catastrophic forgetting：学习新任务时，旧任务性能下降。
- interference：旧任务知识或迁移路径与新任务不匹配时，会阻碍当前任务学习。

作者认为 growable neural networks 通过为新任务增加模块、保留旧参数，可以自然缓解遗忘和干扰，但很多已有方法的参数或推理成本随任务数增长过快，尤其 Progressive Neural Networks 这类方法会在任务数增加时带来较高扩展成本。

*解释一下这个已有方法，每个新任务拥有一整列网络，并且旧任务参数被冻结，通过横向连接使用旧网络的所有特征信息，仅更改横向连接和自身参数
*我认为现在需要解决的问题有俩个，新任务影响旧任务的处理能力，旧任务干扰新任务的学习能力

## 2. CompoNet 的核心思想

CompoNet 是一种可增长的模块化策略网络。每遇到一个新任务，网络新增一个 self-composing policy module，并保留之前任务训练好的模块。新模块不直接共享旧模块内部隐藏层，而是读取旧模块对当前状态产生的策略输出，再通过 attention 机制组合这些旧策略输出，并与自己的 internal policy 结合。

论文强调的关键点是：CompoNet 复用的是先前策略模块的输出，而不是密集连接旧网络内部表示。这使模型可以在任务数增加时保持较好的可扩展性，并保留对新任务的 plasticity。

*output attention 决定旧模块和新模块的权重，在策略输出层面
*input attention 哪些旧模块的信息，参考多少，进入信息输入层面

## 3. 模块结构

论文 Section 4.2 将 self-composing policy module 分成三个主要部分：

- Output attention head：基于当前状态表示 `h_s` 和之前策略输出矩阵 `Phi`，生成一个 tentative output `v`。它对旧策略输出做 scaled dot-product attention，value 直接使用旧策略输出。
- Input attention head：从旧策略输出和 output attention head 的 tentative output 中提取上下文信息，供 internal policy 使用。它的 value 是输入的可学习线性变换，而不是直接返回旧策略输出。
- Internal policy：接收 input attention head 的输出和当前状态表示，用一个 feed-forward network 生成修正向量。该向量与 tentative output 相加，得到当前模块输出；是否再归一化取决于动作空间性质。

因此，论文中的最终直觉是：output attention head 先提出“旧策略能给出的候选行为”，input attention head 提供“旧策略相关上下文”，internal policy 再决定保留、调整或覆盖这个候选行为。

*scaled dot-product attention：缩放点积 如何分配权重？点积大则相关性强 Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
*Q当前状态 K旧模块特征向量 V之前输出
*tentative output：之前所有模块的临时输出V
*context vector 相当于一个中间表示
*feed-forward network 前馈神经网络
*MLP Multi-Layer Perceptron 普通的全连接神经网络

## 4. State Encoding

论文 Section 4.1 讨论 state encoding 的必要性：模块被冻结后，其输入状态分布不应发生不一致变化。

- 对 Atari 这类视觉任务，论文使用 CNN encoder 将 `210 x 160` RGB 图像编码成低维表示。
- 对 Meta-World 这类低维连续控制任务，状态本身是实值向量，因此不需要额外 encoder，可视为 `h_s = s`。
- 论文 Appendix A 讨论了 DINOv2 表示作为视觉 foundation model 的可行性，但结论是：DINO 能产生可用表示，不过在本文小型 Atari 图像任务中，CNN 更快，DINO 更适合极大任务序列或高维视觉输入场景。

*每一个模块处理不同任务，但由于需要参考前面的模块，所以应该转换成相同特征量 神经网络能处理的特征表示

## 5. 可扩展性

论文强调 CompoNet 的参数量随任务数线性增长。原因是每个新任务只新增一个固定大小的 self-composing policy module；每个模块主要包含 attention 相关线性变换和 feed-forward block。

Appendix B 给出内存增长分析，Figure 3 和 Appendix C 讨论推理成本。论文指出理论推理成本相对任务数包含更高阶项，但在最多 300 个任务的经验测试中，CompoNet 的实际推理时间增长表现可接受。相关测量使用 AMD EPYC 7252 CPU 和 NVIDIA A5000 GPU。

## 6. 评价指标

论文 Section 5.1 使用 success rate `p_i(t)` 作为任务性能，范围为 `[0, 1]`。

- Average Performance：所有任务 success rate 的平均值，论文报告最终时刻 `P(T)`。
- Forward Transfer：方法在某任务上的训练曲线相对从零训练 baseline 的归一化面积差。baseline 是每个任务独立从随机初始化训练的 agent。
- Reference forward Transfer (RT)：对每个目标任务，取所有单源 fine-tuning 迁移中最好的 forward transfer，作为理想源任务选择参考。论文指出，组合多个旧任务知识的方法可能超过 RT。

Atari 的 success rate 不是环境直接给出的。Appendix D.4 定义：如果 episodic return 大于等于 success score，则 success 为 1，否则为 0。success score 是所有 8 个方法、10 个随机种子最终 episodic return 平均值的 90%。论文表 D.1 给出了 SpaceInvaders 和 Freeway 的固定 success score。Meta-World 的 success 由环境直接给出。

代码确认点：本地 `experiments/atari/process_results.py` 中 `SETTINGS` 使用 `sc_percent=1.0`，这与论文 D.4 的 90% 表述存在差异，后续处理官方数据或本地 runs 时必须单独核对。

## 7. 实验设置

论文 Section 5.2 和 Appendix D/E 给出三组任务序列：

- Meta-World：10 个机器人操作任务重复两轮，共 20 个任务；状态为 39 维实值向量，动作为 4 维连续向量；使用 SAC；每任务 `1M` timesteps。
- SpaceInvaders：`ALE/SpaceInvaders-v5` 的 10 个 playing modes；图像状态为 RGB frame；使用 CNN encoder 和 PPO；每任务 `1M` timesteps。
- Freeway：正文称 `ALE/Freeway-v5` 的 7 个 playing modes；Appendix D.3 文字描述到 mode 6，但 Appendix D.4 表 D.1b 列出 TASK 0 到 TASK 7。代码 `experiments/atari/task_utils.py` 也使用 modes 0-7。因此这是论文正文/任务描述与附录表格/代码之间的不一致点。

论文比较的方法包括 Baseline、FT-1、FT-N、ProgressiveNet、PackNet 和 CompoNet。结果以 10 random seeds 的均值和标准差报告。

Appendix E 给出的关键超参包括：

- Meta-World/SAC：Adam，discount `0.99`，hidden dimension `256`，batch size `128`，buffer size `1e6`，random actions `1e4`，start learning at `5e3`。
- Atari/PPO：Adam，learning rate `2.5e-4`，discount `0.99`，hidden dimension `512`，8 个并行环境，batch size `1024`，minibatch size `256`，4 个 minibatches，rollout steps `128`。

## 8. 主要结果

Table 1 显示 CompoNet 在三组序列中都取得最高或并列最高的表现：

- Meta-World：CompoNet 的 performance 最高，且是唯一 forward transfer 为正的方法。
- SpaceInvaders：CompoNet 与 FT-N 的 performance 均接近 0.99；CompoNet 的 forward transfer 最高。
- Freeway：CompoNet 的 performance 和 forward transfer 都明显高于其他方法。

论文结论是：CompoNet 能通过组合旧策略获得超过单源 fine-tuning 参考的迁移能力，并且在保持旧模块的同时仍保留学习新任务的能力。

## 9. Attention 与 Ablation

Section 5.4 验证了 CompoNet 在三种场景下的行为：

- 当旧模块中有一个对当前任务有用时，output attention head 会给该模块较高权重。
- 当旧模块都不相关时，CompoNet 可以主要依靠 internal policy 从头学习，避免被无用旧模块严重干扰。
- 论文 Appendix G 进一步做了 attention head ablation：在 Freeway 中去掉 output attention head 会显著降低表现；在特定 SpaceInvaders 设置中，input attention head 也被用于验证其作用。

## 10. 与其他方法的关系

相对 ProgressiveNet，CompoNet 不通过 lateral connections 连接旧模块隐藏层，而是在策略输出层面组合旧模块，因此参数增长更轻。

相对 PackNet，CompoNet 不把所有任务挤入同一个固定容量网络，而是为每个任务增加新模块，因此更强调保持 plasticity。

相对 FT-1/FT-N，CompoNet 不只是延续或保存 fine-tuned 模型，而是学习如何基于当前状态组合多个旧策略输出。

## Verification Notes

- 本文档已基于 `paper/self_composing_policies.pdf` 重新复核。
- 来自论文的内容：CRL 问题定义、CompoNet 三块结构、state encoding、可扩展性分析、Section 5.1 指标、Section 5.2 实验设置、Table 1 结果、Appendix D/E/G 的任务、success score、超参和 ablation。
- 来自代码检查的内容：Freeway 代码任务序列为 0-7；Atari `process_results.py` 中 `sc_percent=1.0`。
- 仍需从代码或实验确认：本地处理脚本如何复现论文表 D.1 的 success score；Atari/Meta-World 保存加载路径；本地依赖环境是否能运行 smoke test。
- 目前仍不确定：Freeway 正文“7 playing modes”和 Appendix D.4/代码 8 个 task 之间应如何在正式复现实验报告中解释。
