# CompoNet 论文理解笔记

论文：Self-Composing Policies for Scalable Continual Reinforcement Learning。

说明：当前本地仓库没有 `paper/self_composing_policies.pdf`，因此本笔记基于官方 PMLR 页面、OpenReview/arXiv HTML 版本、本地 `README.md` 和本地代码结构交叉整理。后续如果补回 PDF，应再核对公式、表格和附录超参。

## 1. 论文要解决的问题

论文关注 Continual Reinforcement Learning (CRL) 中的策略学习：智能体按顺序遇到一串任务，每个任务只有有限交互预算，不能无限重训。目标不是只在当前任务上学好，而是让过去任务学到的策略能帮助未来任务更快学习，同时尽量避免新任务训练破坏旧知识。

作者认为很多 CRL 方法在深度强化学习里有两个困难：

- 旧策略可能有用，但很难自动判断什么时候、以什么比例使用旧策略。
- 如果直接复用或微调旧网络，容易出现遗忘、干扰或参数规模不可扩展。

CompoNet 的目标是让每个新任务自动组合已有策略，而不是手工选择一个源任务或完全从零训练。

## 2. Continual Reinforcement Learning 的背景问题

CRL 假设任务按序列到来。训练任务 `t` 时，模型已经经历了任务 `0...t-1`，但不能重新从头联合训练所有任务。强化学习比监督学习更麻烦，因为数据来自与环境交互，策略变化会改变数据分布；如果新任务预算有限，能否利用旧任务经验会直接影响样本效率。

论文里的核心背景问题包括：

- stability-plasticity trade-off：既要保持旧知识稳定，又要对新任务有足够可塑性。
- transfer：旧任务策略可能加速新任务学习，也可能造成负迁移。
- scalability：任务数增加时，参数量、推理时间和训练复杂度不能爆炸式增长。

## 3. catastrophic forgetting 和 interference

catastrophic forgetting 指训练新任务时，模型参数被更新后，旧任务性能显著下降。Fine-tuning 类方法最容易出现这种问题，因为同一套参数持续被新任务覆盖。

interference 在这篇论文里更偏向旧任务知识对新任务学习造成的负面影响：旧策略、共享参数或迁移路径如果与当前任务不匹配，会阻碍当前任务收敛，导致学习速度慢或最终性能差。论文也通过 Forward Transfer / Reference Transfer 讨论旧任务到新任务的正负迁移。

## 4. CompoNet 的核心思想

CompoNet 把策略序列组织成一组 self-composing policy modules。第一个任务训练一个普通策略模块；之后每来一个新任务，就新增一个模块。新模块不覆盖旧模块，而是读取旧模块对当前状态的策略输出，并通过 attention 机制选择、组合这些旧策略，再与自身 internal policy 的输出相加得到当前任务策略。

直观理解：旧策略是一个可查询的策略库，新任务模块学习“当前状态下哪些旧策略有用、应该组合多少、还需要自己补充什么”。

## 5. 每个新任务到来时，网络结构如何增长

第一个任务用 `FirstModuleWrapper` 包装一个普通策略网络。之后任务 `t` 到来时：

- 创建一个新的 CompoNet unit。
- 新 unit 接收所有历史 unit 作为 `previous_units`。
- 历史 unit 对当前 state 产生策略输出矩阵 `Phi`。
- 新 unit 有自己的 encoder、output attention head、input attention head 和 internal policy。
- 新 unit 的输出也会追加到 `Phi`，供未来任务使用。

因此模型随任务数线性增长：每个任务新增一个模块，但旧模块不再训练。

## 6. 旧模块如何被冻结

本地 `componet/impl.py` 中，新建 `CompoNet` 时会遍历 `previous_units`：

- 删除更旧的嵌套 `previous_units` 引用，避免重复持有历史链。
- 设置 `unit.is_prev = True`。
- 调用 `unit.eval()`。
- 将旧模块所有参数的 `requires_grad` 设为 `False`。

这意味着旧模块只做前向推理，不参与当前任务梯度更新，从机制上避免新任务训练直接破坏旧任务参数。

## 7. 新模块如何组合旧策略和内部策略

对当前状态 `s`，encoder 先得到 state representation `h_s`。所有旧模块对该状态输出策略向量，形成矩阵 `Phi`。

新模块先用 output attention head 从旧策略输出中得到一个组合结果 `out_head`。然后把 `Phi` 和 `out_head` 拼在一起，输入 input attention head，得到一个面向 internal policy 的上下文向量。internal policy 接收这个上下文向量和 `h_s`，输出新任务自己的 logits 或动作分布修正项。

最终输出为：

```text
current_policy_output = output_attention_result + internal_policy_output
```

如果设置 `ret_probs=True`，最终输出再经过 softmax 变为概率。

## 8. state encoding 的作用

state encoding 是把原始状态变成适合 attention 和策略网络使用的特征表示。对 Atari，原始输入是图像帧，代码里有 CNN encoder 和 DINO encoder 相关实现；对 Meta-World，输入是低维连续状态。

state encoding 作为 attention query 的来源，使新模块能根据当前状态动态决定旧策略的组合方式，而不是对所有状态使用固定权重。

## 9. output attention head 的作用

output attention head 直接在旧策略输出空间上做组合。它用当前 state encoding 生成 query，用旧策略输出加 positional encoding 后生成 key，value 是旧策略输出本身。得到的 attention 权重表示当前状态下每个旧策略对最终动作分布或 logits 的贡献。

它的作用是产生一个可执行的“旧策略混合输出”，相当于从历史策略库中动态选取有用策略。

## 10. input attention head 的作用

input attention head 不直接给最终动作，而是为 internal policy 提供上下文。它读取旧策略输出以及 output attention head 的组合结果，生成一个 hidden context，再和 state encoding 拼接后输入 internal policy。

它的作用是告诉 internal policy：当前状态下，历史策略已经提供了哪些行为倾向，新模块还需要补充或修正什么。

## 11. internal policy 的作用

internal policy 是当前任务新增模块自己的可训练策略网络。它承担当前任务特有行为的学习，尤其是在旧策略不足、旧策略冲突或需要新技能时提供修正。因为最终输出是旧策略组合结果加 internal policy 输出，所以它既能利用旧策略，又不被旧策略完全限制。

## 12. 实验环境

论文和代码覆盖三类序列：

- Meta-World：10 个机器人操作任务，代码中 `experiments/meta-world/tasks.py` 将 10 个任务重复两轮，共 20 个 task id，用于检验第二轮是否能利用第一轮任务知识。
- Atari SpaceInvaders：ALE `SpaceInvaders` 的不同 mode，代码中为 `ALE/SpaceInvaders-v5` 的 mode 0-9。
- Atari Freeway：ALE `Freeway` 的不同 mode。论文计划中提到 Freeway modes 0-6，但本地 `experiments/atari/task_utils.py` 写的是 0-7 共 8 个 mode，这是一个需要后续核对的论文/代码差异。

README 只说明 Atari 实验在 `experiments/atari/`，Meta-World 实验在 `experiments/meta-world/`，并没有列出完整任务序列；具体序列需要看代码和论文。

## 13. baseline

论文和代码中涉及的主要方法包括：

- Baseline / from scratch：每个任务从头训练独立策略，不利用旧任务。
- Fine-tuning：在旧模型基础上继续训练当前任务，代码里 Atari 名为 `cnn-simple-ft`，Meta-World 名为 `finetune`。
- ProgressiveNet：为新任务新增列，通过 lateral connection 使用旧列，旧列冻结。
- PackNet：通过参数剪枝/掩码把不同任务打包到同一网络中，减少遗忘但容量和可塑性受约束。
- CompoNet：本文方法，自组合旧策略并新增当前任务模块。

论文还讨论 FT-1 和 FT-N 的概念：FT-1 只从一个旧任务迁移，FT-N 使用多旧任务迁移设置，用于研究旧任务选择和干扰。

## 14. 评价指标

主要指标包括：

- Average Performance：各任务最终性能平均值。Meta-World 主要看 success，Atari 从 episodic return 计算 success。
- Forward Transfer：比较某方法在新任务上的学习曲线是否优于从零训练 baseline，衡量旧知识对新任务学习速度和性能的帮助。
- Reference Transfer：对每个目标任务，参考所有单源迁移中的最好迁移效果，衡量多任务方法能否接近或超过“知道最佳源任务”的理想选择。

Atari 中 success score 由 episodic return 曲线派生：代码 `process_results.py` 根据各算法后段平均 return 的一定比例计算阈值，再把 return 是否超过阈值转成 success 曲线。Meta-World 环境直接在 `info["success"]` 中提供 success。

## 15. 论文主要结论

论文主要结论是：CompoNet 能在不改写旧模块的情况下复用历史策略，并在 Atari 和 Meta-World 序列中取得较好的平均性能和 forward transfer。它特别适合旧任务之间存在可复用技能但任务差异又足够大、不能简单共享同一策略的场景。

实验结论可概括为：

- CompoNet 通常比 fine-tuning 更抗遗忘和负迁移。
- CompoNet 比 ProgressiveNet 更可扩展，因为每个模块不需要连接所有旧网络内部层。
- CompoNet 比 PackNet 更保持新任务可塑性，因为它不是在固定容量网络中不断分配稀疏子网络。
- attention 可解释性实验显示，新模块确实会对不同旧策略分配不同权重。

## 16. 相对 Progressive Neural Networks / PackNet / fine-tuning 的优势

相对 Progressive Neural Networks：

- CompoNet 组合的是旧策略输出，而不是密集连接旧网络内部表示，结构更轻。
- 参数量和推理成本随任务增长更可控。
- 新模块通过 attention 在策略层面选择旧知识，更接近“组合技能”。

相对 PackNet：

- PackNet 通过固定网络容量中的掩码/剪枝保存旧任务，任务越多可用容量越紧张。
- CompoNet 每任务新增模块，旧模块冻结，避免在同一参数空间里争抢容量。
- CompoNet 更适合持续加入新任务时保持 plasticity。

相对 fine-tuning：

- Fine-tuning 容易直接覆盖旧任务参数，引发 catastrophic forgetting。
- Fine-tuning 如果源任务不合适会造成 interference。
- CompoNet 不更新旧模块，而是学习如何组合旧策略和当前任务 internal policy，因此能降低遗忘，并减少对单个源任务选择的依赖。

